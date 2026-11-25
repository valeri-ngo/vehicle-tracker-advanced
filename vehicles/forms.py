from datetime import datetime
from typing import Any

from django import forms
from django.utils import timezone

from .models import OdometerEntry, Vehicle
from .validators import validate_odometer_entry


class VehicleCreateForm(forms.ModelForm):
    """Handle the registration of a new vehicle.

    Allow the user to provide vehicle details and an initial mileage
    reading when adding a vehicle to their account.
    """

    class Meta:
        model = Vehicle
        fields = (
            "brand",
            "model",
            "year",
            "current_mileage",
        )


class VehicleUpdateForm(forms.ModelForm):
    """Allow users to update the identification details of an existing vehicle.

    Exclude the current mileage to ensure that mileage changes are
    recorded through the odometer history.
    """

    class Meta:
        model = Vehicle
        fields = (
            "brand",
            "model",
            "year",
        )


class OdometerEntryForm(forms.ModelForm):
    class OdometerEntryForm(forms.ModelForm):
        """Handle the submission of odometer readings for a specific vehicle.

        Reject future timestamps and validate mileage against the existing
        odometer history to maintain chronological consistency.
        """

    class Meta:
        model = OdometerEntry
        fields = (
            "mileage",
            "recorded_at",
        )

    def __init__(self, *args: Any, vehicle: Vehicle, **kwargs: Any) -> None:
        """Initialize the form with the vehicle used for mileage validation."""

        super().__init__(*args, **kwargs)
        self.vehicle = vehicle

    def clean_recorded_at(self) -> datetime:
        """Validate the recording timestamp and reject future dates."""

        recorded_at = self.cleaned_data["recorded_at"]

        if recorded_at > timezone.now():
            raise forms.ValidationError("The recorded date cannot be in the future.")

        return recorded_at

    def clean(self) -> dict[str, Any]:
        """Validate the submitted mileage against the vehicle's odometer history.

        Skip chronological validation if either required field has failed
        field-level validation. Attach any detected errors to the relevant fields.
        """

        cleaned_data = super().clean() or self.cleaned_data

        mileage = cleaned_data.get("mileage")
        recorded_at = cleaned_data.get("recorded_at")

        if mileage is None or recorded_at is None:
            return cleaned_data

        errors = validate_odometer_entry(
            vehicle=self.vehicle,
            mileage=mileage,
            recorded_at=recorded_at,
        )

        for field, message in errors:
            self.add_error(field, message)

        return cleaned_data
