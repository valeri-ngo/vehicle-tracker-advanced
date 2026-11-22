from django.db import models


class ServiceDetailsModel(models.Model):
    """Define common fields shared by service records and maintenance schedules."""

    class ServiceType(models.TextChoices):
        """Define the available vehicle maintenance service types."""

        OIL_CHANGE = "oil_change", "Oil change"
        FILTERS = "filters", "Filters"
        BRAKES = "brakes", "Brakes"
        TIMING_BELT = "timing_belt", "Timing belt / Chain"
        TIRES = "tires", "Tires"
        SUSPENSION = "suspension", "Suspension"
        TRANSMISSION = "transmission", "Transmission"
        COOLING = "cooling", "Cooling System"
        REPAIR = "repair", "General Repair"
        OTHER = "other", "Other"

    service_type = models.CharField(
        max_length=30,
        choices=ServiceType,
    )

    description = models.TextField(
        blank=True,
    )

    class Meta:
        abstract = True
