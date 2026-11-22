from datetime import timedelta

from django.db import models
from django.utils import timezone

from vehicles.models import Vehicle


class VehicleDocument(models.Model):
    class DocumentType(models.TextChoices):
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

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ("expires_on",)

    def __str__(self):
        return f"{self.vehicle} - {self.get_document_type_display()}"

    @property
    def is_expired(self):
        return timezone.localdate() > self.expires_on

    @property
    def reminder_due(self):
        today = timezone.localdate()

        reminder_date = self.expires_on - timedelta(
            days=self.reminder_days_before,
        )

        return self.notifications_enabled and reminder_date <= today <= self.expires_on
