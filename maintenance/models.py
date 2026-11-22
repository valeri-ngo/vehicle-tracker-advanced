from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class ServiceRecord(models.Model):
    class ServiceType(models.TextChoices):
        OIL_CHANGE = "oil_change", "Oil change"
        FILTERS = "filters", "Filters"
        BRAKES = "brakes", "Brakes"
        TIMING_BELT = "timing_belt", "Timing belt / Chain"
        TIRES = "tires", "Tires"
        SUSPENSION = "suspension", "Suspension"
        TRANSMISSION = "transmission", "Transmission"
        COOLING = "cooling", "Cooling System"
        REPAIR = "repair", "General Repair"
        Other = "other", "Other"

    vehicle = models.ForeignKey(
        to="vehicles.Vehicle",
        on_delete=models.CASCADE,
        related_name="service_records",
    )

    service_type = models.CharField(
        max_length=30,
        choices=ServiceType,
    )

    description = models.TextField(
        blank=True,
    )

    mileage = models.PositiveIntegerField()

    service_date = models.DateField()

    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.vehicle} - {self.service_type}"

    class Meta:
        ordering = ("-service_date",)


class MaintenanceSchedule(models.Model):
    vehicle = models.ForeignKey(
        to="vehicles.Vehicle",
        on_delete=models.CASCADE,
        related_name="maintenance_schedules",
    )

    service_type = models.CharField(
        max_length=30,
        choices=ServiceRecord.ServiceType,
    )

    description = models.TextField(
        blank=True,
    )

    due_date = models.DateField(
        null=True,
        blank=True,
    )

    due_mileage = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    is_completed = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.vehicle} - {self.get_service_type_display()}"
