from django import forms
from django.utils import timezone

from .models import OdometerEntry, Vehicle


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
        cleaned_data = super().clean() or self.cleaned_data

        mileage = cleaned_data.get("mileage")
        recorded_at = cleaned_data.get("recorded_at")

        if mileage is None or recorded_at is None:
            return cleaned_data

        entries = self.vehicle.odometer_entries

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
            self.add_error("mileage", "Mileage cannot be lower than the previous one.")

        if next_entry is not None and mileage > next_entry.mileage:
            self.add_error("mileage", "Mileage cannot be higher than the next one.")

        if entries.filter(recorded_at=recorded_at).exists():
            self.add_error(
                "recorded_at",
                "An odometer entry already exists for this date and time.",
            )

        if not entries.exists() and mileage < self.vehicle.current_mileage:
            self.add_error(
                "mileage", "Mileage cannot be lower than the existing vehicle mileage."
            )
        return cleaned_data
