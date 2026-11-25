from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from common.basic_models import CreatedAtModel
from maintenance.helpers.abstract_models import ServiceDetailsModel


class ServiceRecord(ServiceDetailsModel, CreatedAtModel):
    """Represent a completed maintenance operation for a vehicle.

    Store the service date, recorded mileage, cost and associated parts
    as part of the vehicle's service history.
    """

    vehicle = models.ForeignKey(
        to="vehicles.Vehicle",
        on_delete=models.CASCADE,
        related_name="service_records",
    )

    mileage = models.PositiveIntegerField()

    service_date = models.DateField()

    parts = models.ManyToManyField(
        "Part",
        blank=True,
        related_name="service_records",
    )

    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )

    def __str__(self) -> str:
        """Return the vehicle and service type as a readable string."""

        return f"{self.vehicle} - {self.get_service_type_display()}"

    class Meta:
        ordering = ("-service_date",)
        constraints = (
            models.CheckConstraint(
                condition=models.Q(cost__gte=0),
                name="service_record_cost_non_negative",
            ),
        )


class MaintenanceSchedule(ServiceDetailsModel, CreatedAtModel):
    """Represent a planned maintenance operation for a vehicle.

    Schedule maintenance by date, mileage or both, and track whether
    the required service has been completed.
    """

    vehicle = models.ForeignKey(
        to="vehicles.Vehicle",
        on_delete=models.CASCADE,
        related_name="maintenance_schedules",
    )

    due_date = models.DateField(
        null=True,
        blank=True,
    )

    due_mileage = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    parts = models.ManyToManyField(
        "Part",
        blank=True,
        related_name="maintenance_schedules",
    )

    is_completed = models.BooleanField(
        default=False,
    )

    def __str__(self) -> str:
        """Return the vehicle and scheduled service type as a readable string."""

        return f"{self.vehicle} - {self.get_service_type_display()}"

    class Meta:
        ordering = ("-created_at",)
        constraints = (
            models.CheckConstraint(
                condition=(
                    models.Q(due_date__isnull=False)
                    | models.Q(due_mileage__isnull=False)
                ),
                name="maintenance_schedule_requires_date_or_mileage",
            ),
        )


class Part(CreatedAtModel):
    """Represent a reusable part in the user's personal parts catalog.

    Allow the same catalog entry to be associated with multiple service
    records and maintenance schedules.
    """

    owner = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="parts",
    )

    name = models.CharField(
        max_length=100,
    )

    manufacturer = models.CharField(
        max_length=100,
        blank=True,
    )

    part_number = models.CharField(
        max_length=100,
        blank=True,
    )

    def __str__(self) -> str:
        """Return the part name as its string representation."""

        return self.name
