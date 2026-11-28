from typing import Any

from django.utils import timezone

from accounts.models import Account
from common.quotas import get_subscription_plan
from documents.models import VehicleDocument
from maintenance.models import MaintenanceSchedule
from notifications.models import Notification
from vehicles.models import Vehicle


def build_document_reminder_key(document: VehicleDocument) -> str:
    """Build a deterministic deduplication key for a document reminder.

    Ensure that repeated reminder checks do not create duplicate
    notifications for the same document and expiration date.
    """
    return f"document:{document.id}:{document.expires_on.isoformat()}:expiry"


def create_document_reminder(
    document: VehicleDocument,
) -> tuple[Notification | None, bool]:
    """Create an expiration reminder for an eligible vehicle document.

    Enforce subscription-based reminder periods and vehicle restrictions.
    Prevent duplicate notifications for the same document and expiration date.

    Return the notification and whether it was newly created,
    or (None, False) when the document is not eligible.
    """

    owner = document.vehicle.owner

    if not owner.has_perm("documents.use_document_reminders"):
        return None, False

    reminder_days_before: int = 7

    if owner.has_perm("documents.customize_document_reminders"):
        reminder_days_before = document.reminder_days_before

    if not document.is_reminder_due(reminder_days_before):
        return None, False

    subscription_plan: str = get_subscription_plan(owner)

    if subscription_plan == "Free":
        first_vehicle_id: int | None = (
            Vehicle.objects.filter(
                owner=owner,
            )
            .order_by(
                "pk",
            )
            .values_list(
                "pk",
                flat=True,
            )
            .first()
        )

        if first_vehicle_id != document.vehicle_id:
            return None, False

    key = build_document_reminder_key(document)
    defaults = _build_document_reminder_defaults(document, owner)

    Notification(
        **defaults,
        deduplication_key=key,
    ).full_clean(validate_unique=False)

    notification, created = Notification.objects.get_or_create(
        defaults=defaults,
        deduplication_key=key,
    )

    return notification, created


def _build_document_reminder_defaults(
    document: VehicleDocument,
    owner: Account,
) -> dict[str, Any]:
    """Prepare the notification data for a document expiration reminder."""

    document_type = document.get_document_type_display()

    return {
        "recipient": owner,
        "notification_type": Notification.NotificationTypes.DOCUMENT,
        "title": f"{document_type} expiration",
        "message": f"{document_type} - {document.expires_on.isoformat()}",
        "document": document,
    }


def generate_document_reminders() -> int:
    """Generate due document reminders and return the number created.

    Process documents with enabled notifications while respecting
    reminder permissions and deduplication rules.
    """

    documents = VehicleDocument.objects.filter(
        notifications_enabled=True,
        expires_on__gte=timezone.localdate(),
    ).select_related("vehicle__owner")

    created_count = 0

    for document in documents.iterator():
        _, created = create_document_reminder(document)

        if created:
            created_count += 1

    return created_count


def create_maintenance_reminder(
    schedule: MaintenanceSchedule,
) -> tuple[Notification | None, bool]:
    """Create a reminder for an eligible maintenance schedule.

    Respect maintenance scheduling permissions and prevent duplicate
    notifications for the same scheduled service.

    Return the notification and whether it was newly created,
    or (None, False) when the schedule is not eligible.
    """

    owner: Account = schedule.vehicle.owner

    if not owner.has_perm("maintenance.manage_maintenance_schedules"):
        return None, False

    if not schedule.is_reminder_due():
        return None, False

    status: str = _get_maintenance_reminder_status(schedule)
    key: str = build_maintenance_reminder_key(schedule, status)

    defaults: dict[str, Any] = _build_maintenance_reminder_defaults(
        schedule, owner, status
    )

    Notification(
        **defaults,
        deduplication_key=key,
    ).full_clean(validate_unique=False)

    notification, created = Notification.objects.get_or_create(
        defaults=defaults,
        deduplication_key=key,
    )

    return notification, created


def build_maintenance_reminder_key(
    schedule: MaintenanceSchedule,
    status: str,
) -> str:
    """Build a deterministic deduplication key for a maintenance reminder."""

    due_date: str = (
        schedule.due_date.isoformat() if schedule.due_date is not None else "none"
    )

    due_mileage: str = (
        str(schedule.due_mileage) if schedule.due_mileage is not None else "none"
    )

    return f"maintenance:{schedule.pk}:{due_date}:{due_mileage}:{status}"


def generate_maintenance_reminders() -> int:
    """Generate due maintenance reminders and return the number created.

    Process incomplete maintenance schedules while respecting
    subscription permissions and deduplication rules.
    """

    schedules = MaintenanceSchedule.objects.filter(
        is_completed=False,
    ).select_related("vehicle__owner")

    created_count: int = 0

    for schedule in schedules.iterator():
        _, created = create_maintenance_reminder(schedule)

        if created:
            created_count += 1

    return created_count


def _get_maintenance_reminder_status(schedule: MaintenanceSchedule) -> str:
    """Determine the reminder status of an eligible maintenance schedule."""

    if schedule.is_overdue:
        return "overdue"

    elif schedule.is_due:
        return "due"

    return "upcoming"


def _build_maintenance_reminder_defaults(
    schedule: MaintenanceSchedule,
    owner: Account,
    status: str,
) -> dict[str, Any]:
    """Prepare notification data for a scheduled maintenance reminder."""

    service_type: str = schedule.get_service_type_display()
    title: str = f"{status.capitalize()}: {service_type}"
    message_parts: list[str] = [f"{schedule.vehicle} - {service_type}."]

    if schedule.due_date is not None:
        message_parts.append(f"Due date: {schedule.due_date.isoformat()}.")

    if schedule.due_mileage is not None:
        message_parts.append(f"Due mileage: {schedule.due_mileage} km.")

    message: str = " ".join(message_parts)

    return {
        "recipient": owner,
        "notification_type": Notification.NotificationTypes.MAINTENANCE,
        "title": title,
        "message": message,
        "maintenance_schedule": schedule,
    }
