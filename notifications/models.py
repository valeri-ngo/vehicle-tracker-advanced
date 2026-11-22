from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from common.basic_models import DateTimeModel


class Notification(DateTimeModel):
    class NotificationTypes(models.TextChoices):
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

    def __str__(self):
        return self.title

    def clean(self):
        """Validate notification type, related objects, and recipient ownership."""

        super().clean()
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

        if (
            self._state.adding
            and self.notification_type == self.NotificationTypes.DOCUMENT
            and self.document_id is None
        ):
            raise ValidationError("Document notifications must have a document.")

        if (
            self._state.adding
            and self.notification_type == self.NotificationTypes.MAINTENANCE
            and self.maintenance_schedule_id is None
        ):
            raise ValidationError(
                "Maintenance notifications must have a maintenance schedule."
            )
