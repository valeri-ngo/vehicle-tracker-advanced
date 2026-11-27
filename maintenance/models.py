from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Lower

from common.basic_models import CreatedAtModel
from maintenance.helpers.abstract_models import ServiceDetailsModel


class ServiceRecord(ServiceDetailsModel, CreatedAtModel):
    """Represent a completed maintenance operation for a vehicle.

    Store the service date, recorded mileage, cost and selected maintenance
    items as part of the vehicle's service history.
    """

    vehicle = models.ForeignKey(
        to="vehicles.Vehicle",
        on_delete=models.CASCADE,
        related_name="service_records",
    )

    mileage = models.PositiveIntegerField()

    service_date = models.DateField()

    maintenance_items = models.ManyToManyField(
        "MaintenanceItem",
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

    maintenance_items = models.ManyToManyField(
        "MaintenanceItem",
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
        permissions = (
            (
                "manage_maintenance_schedules",
                "Can manage maintenance schedules.",
            ),
        )


class MaintenanceItem(CreatedAtModel):
    """Represent a reusable vehicle maintenance checklist item.

    Provide predefined maintenance items available to all users and custom
    items owned by individual users. Allow items to be associated with
    completed service records and planned maintenance schedules.
    """

    class CategoryType(models.TextChoices):
        """Define categories for vehicle maintenance items."""

        OIL_FILTERS = "oil_filters", "Oil & Filters"
        BRAKES = "brakes", "Braking System"
        ENGINE = "engine", "Engine"
        COOLING = "cooling", "Cooling System"
        TRANSMISSION = "transmission", "Transmission"
        SUSPENSION = "suspension", "Suspension & Steering"
        ELECTRICAL = "electrical", "Electrical System"
        TIRES = "tires", "Wheels & Tires"
        EXHAUST = "exhaust", "Exhaust System"
        AIR_CONDITIONING = "air_conditioning", "Air Conditioning"
        BODY = "body", "Body & Exterior"
        OTHER = "other", "Other"

    owner = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="maintenance_items",
    )

    name = models.CharField(
        max_length=100,
    )

    category = models.CharField(
        max_length=50,
        choices=CategoryType,
    )

    class Meta:
        ordering = ("category", "name")

        constraints = (
            models.UniqueConstraint(
                Lower("name"),
                condition=models.Q(owner__isnull=True),
                name="unique_standard_maintenance_item",
            ),
            models.UniqueConstraint(
                Lower("name"),
                models.F("owner"),
                condition=models.Q(owner__isnull=False),
                name="unique_custom_maintenance_item_per_owner",
            ),
        )

    def is_in_use(self) -> bool:
        """Determine whether the item is associated with any maintenance records."""

        has_service_records: bool = self.service_records.exists()

        has_maintenance_schedules: bool = self.maintenance_schedules.exists()

        return has_service_records or has_maintenance_schedules

    def __str__(self) -> str:
        """Return the maintenance item name as its string representation."""

        return self.name
