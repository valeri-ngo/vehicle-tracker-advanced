from django import forms
from django.utils import timezone

from .models import OdometerEntry, Vehicle
from .validators import validate_odometer_entry


class VehicleCreateForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = (
            "brand",
            "model",
            "year",
            "current_mileage",
        )


class VehicleUpdateForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = (
            "brand",
            "model",
            "year",
        )


class OdometerEntryForm(forms.ModelForm):
    class Meta:
        model = OdometerEntry
        fields = (
            "mileage",
            "recorded_at",
        )

    def __init__(self, *args, vehicle: Vehicle, **kwargs):
        super().__init__(*args, **kwargs)
        self.vehicle = vehicle

    def clean_recorded_at(self):
        recorded_at = self.cleaned_data["recorded_at"]

        if recorded_at > timezone.now():
            raise forms.ValidationError("The recorded date cannot be in the future.")

        return recorded_at

    def clean(self):
        """Validate the chronological consistency of the submitted mileage."""

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
