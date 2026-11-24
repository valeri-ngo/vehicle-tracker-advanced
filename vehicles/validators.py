from datetime import datetime

from .models import Vehicle


def validate_odometer_entry(
    vehicle: Vehicle, mileage: int, recorded_at: datetime
) -> list[tuple[str, str]]:
    """Validate the chronological consistency of an odometer entry."""

    errors: list[tuple[str, str]] = []

    entries = vehicle.odometer_entries

    previous_entry = (
        entries.filter(recorded_at__lt=recorded_at)
        .order_by("-recorded_at", "-pk")
        .first()
    )

    next_entry = (
        entries.filter(recorded_at__gt=recorded_at)
        .order_by("recorded_at", "pk")
        .first()
    )

    if previous_entry is not None and mileage < previous_entry.mileage:
        errors.append(("mileage", "Mileage cannot be lower than the previous one."))

    if next_entry is not None and mileage > next_entry.mileage:
        errors.append(("mileage", "Mileage cannot be higher than the next one."))

    if entries.filter(recorded_at=recorded_at).exists():
        errors.append(
            (
                "recorded_at",
                "An odometer entry already exists for this date and time.",
            )
        )

    if not entries.exists() and mileage < vehicle.current_mileage:
        errors.append(
            ("mileage", "Mileage cannot be lower than the existing vehicle mileage.")
        )
    return errors
