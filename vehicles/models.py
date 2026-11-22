from django.conf import settings
from django.db import models
from django.utils import timezone

from common.basic_models import CreatedAtModel


class Vehicle(CreatedAtModel):
    owner = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vehicles",
    )

    brand = models.CharField(
        max_length=50,
    )

    model = models.CharField(
        max_length=50,
    )

    year = models.PositiveSmallIntegerField()

    current_mileage = models.PositiveIntegerField(
        default=0,
    )

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"


class OdometerEntry(CreatedAtModel):
    vehicle = models.ForeignKey(
        to="Vehicle",
        on_delete=models.CASCADE,
        related_name="odometer_entries",
    )

    mileage = models.PositiveIntegerField()

    recorded_at = models.DateTimeField(
        default=timezone.now,
    )

    class Meta:
        ordering = ("-recorded_at",)
        constraints = (
            models.UniqueConstraint(
                fields=["vehicle", "recorded_at"],
                name="unique_vehicle_odometer_recorded_at",
            ),
        )

    def __str__(self):
        return f"{self.vehicle.brand} {self.vehicle.model} ({self.vehicle.year}) - {self.mileage} km"
