from datetime import timedelta

from django.db import models
from django.utils import timezone

from common.basic_models import CreatedAtModel
from vehicles.models import Vehicle


class VehicleDocument(CreatedAtModel):
    """Represent document metadata associated with a vehicle.

    Track expiration dates and reminder preferences without storing
    actual document files.
    """

    class DocumentType(models.TextChoices):
        """Define the supported vehicle document categories."""

        VEHICLE_INSURANCE = "vehicle_insurance", "Vehicle Insurance"
        CASCO_INSURANCE = "casco", "Casco Insurance"
        TECHNICAL_INSPECTION = "inspection", "Technical Inspection"
        VIGNETTE = "vignette", "Vignette"
        VEHICLE_TAX = "vehicle_tax", "Vehicle Tax"
        OTHER = "other", "Other"

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    document_type = models.CharField(
        max_length=30,
        choices=DocumentType,
    )

    expires_on = models.DateField()

    reminder_days_before = models.PositiveSmallIntegerField(
        default=7,
    )

    notes = models.TextField(
        blank=True,
    )

    notifications_enabled = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ("expires_on",)
        permissions = (
            (
                "use_document_reminders",
                "Can use automatic reminders.",
            ),
            (
                "customize_document_reminders",
                "Can customize document reminder periods.",
            ),
        )

    def __str__(self) -> str:
        """Return the vehicle and document type as a readable string."""

        return f"{self.vehicle} - {self.get_document_type_display()}"

    @property
    def is_expired(self) -> bool:
        """Determine whether the document's expiration date has passed."""

        return timezone.localdate() > self.expires_on

    @property
    def reminder_due(self) -> bool:
        """Determine whether the document is within its active reminder window.

        Reminders are due only when notifications are enabled and the
        expiration date has not passed.
        """

        return self.is_reminder_due(self.reminder_days_before)

    def is_reminder_due(self, days_before: int) -> bool:
        """Determine whether the document is within the specified reminder window."""

        today = timezone.localdate()

        reminder_date = self.expires_on - timedelta(
            days=days_before,
        )

        return self.notifications_enabled and reminder_date <= today <= self.expires_on
