from django.conf import settings
from django.db import models
from django.utils import timezone


class Vehicle(models.Model):
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

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"


class OdometerEntry(models.Model):
    vehicle = models.ForeignKey(
        to="Vehicle",
        on_delete=models.CASCADE,
        related_name="odometer_entries",
    )

    mileage = models.PositiveIntegerField()

    recorded_at = models.DateTimeField(
        default=timezone.now,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["vehicle", "recorded_at"],
                name="unique_vehicle_odometer_recorded_at",
            ),
        )

    def __str__(self):
        return f"{self.vehicle.brand} {self.vehicle.model} ({self.vehicle.year}) - {self.mileage} km"
