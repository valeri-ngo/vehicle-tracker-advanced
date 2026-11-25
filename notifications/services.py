from typing import Any

from django.utils import timezone

from accounts.models import Account
from documents.models import VehicleDocument
from notifications.models import Notification


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

    Respect the owner's reminder permission and prevent duplicate
    notifications for the same document and expiration date.

    Return the notification and whether it was newly created,
    or (None, False) when the document is not eligible.
    """

    if not document.reminder_due:
        return None, False

    owner = document.vehicle.owner

    if not owner.has_perm("documents.use_document_reminders"):
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
