from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from common.basic_models import DateTimeModel


class Notification(DateTimeModel):
    """Represent a notification delivered to a vehicle owner.

    Support document and maintenance reminders, prevent duplicate
    notifications through deduplication keys, and preserve notification
    history when related records are deleted.
    """

    class NotificationTypes(models.TextChoices):
        """Define the supported notification categories."""

        DOCUMENT = "document", "Document"
        MAINTENANCE = "maintenance", "Maintenance"

    recipient = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NotificationTypes,
    )

    title = models.CharField(
        max_length=100,
    )

    message = models.TextField()

    document = models.ForeignKey(
        "documents.VehicleDocument",
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
    )

    maintenance_schedule = models.ForeignKey(
        "maintenance.MaintenanceSchedule",
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
    )

    deduplication_key = models.CharField(
        max_length=200,
        unique=True,
        null=True,
        blank=True,
    )

    is_read = models.BooleanField(
        default=False,
    )

    def __str__(self) -> str:
        """Return the notification title as a readable string."""

        return self.title

    def clean(self) -> None:
        """Validate notification type, related objects, and recipient ownership."""

        super().clean()

        self._validate_notification_type()
        self._validate_recipient_ownership()
        self._validate_required_relation()

    def _validate_notification_type(self) -> None:
        """Ensure related objects match the notification type."""

        if (
            self.notification_type == self.NotificationTypes.DOCUMENT
            and self.maintenance_schedule_id is not None
        ):
            raise ValidationError(
                "Document notifications cannot have a maintenance schedule."
            )

        elif (
            self.notification_type == self.NotificationTypes.MAINTENANCE
            and self.document_id is not None
        ):
            raise ValidationError("Maintenance notifications cannot have a document.")

    def _validate_recipient_ownership(self) -> None:
        """Ensure the recipient owns the related document or maintenance schedule."""

        if (
            self.document_id is not None
            and self.document.vehicle.owner_id != self.recipient_id
        ):
            raise ValidationError("The recipient is not the owner of the document.")

        if (
            self.maintenance_schedule_id is not None
            and self.maintenance_schedule.vehicle.owner_id != self.recipient_id
        ):
            raise ValidationError(
                "The recipient is not the owner of the maintenance schedule."
            )

    def _validate_required_relation(self) -> None:
        """Require a matching related object when creating a notification.

        Allow existing notifications to remain valid after their
        related records have been deleted.
        """

        if not self._state.adding:
            return

        if (
            self.notification_type == self.NotificationTypes.DOCUMENT
            and self.document_id is None
        ):
            raise ValidationError("Document notifications must have a document.")

        if (
            self.notification_type == self.NotificationTypes.MAINTENANCE
            and self.maintenance_schedule_id is None
        ):
            raise ValidationError(
                "Maintenance notifications must have a maintenance schedule."
            )
