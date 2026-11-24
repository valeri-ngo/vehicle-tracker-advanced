from typing import ClassVar

from django import forms
from django.utils import timezone

from maintenance.form_mixins import UserPartsQuerysetMixin
from maintenance.models import MaintenanceSchedule, Part, ServiceRecord


class ServiceRecordForm(UserPartsQuerysetMixin, forms.ModelForm):
    """Validate and manage service record form data."""

    class Meta:
        model = ServiceRecord
        fields = (
            "service_type",
            "description",
            "mileage",
            "service_date",
            "cost",
            "parts",
        )
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "service_date": forms.DateInput(
                attrs={
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
            "parts": forms.CheckboxSelectMultiple(),
        }

    def clean_service_date(self):
        """Ensure the service date is not in the future."""

        service_date = self.cleaned_data["service_date"]

        if service_date > timezone.localdate():
            raise forms.ValidationError("Service date cannot be in the future.")

        return service_date


class MaintenanceScheduleForm(UserPartsQuerysetMixin, forms.ModelForm):
    """Validate and manage maintenance schedule form data."""

    class Meta:
        model = MaintenanceSchedule
        fields = (
            "service_type",
            "description",
            "due_date",
            "due_mileage",
            "is_completed",
            "parts",
        )

        widgets: ClassVar[dict[str, forms.Widget]] = {
            "due_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "parts": forms.CheckboxSelectMultiple(),
        }

    def clean(self):
        """Require at least a due date or a due mileage."""

        cleaned_data = super().clean()

        due_date = cleaned_data.get("due_date")
        due_mileage = cleaned_data.get("due_mileage")

        if not due_date and due_mileage is None:
            raise forms.ValidationError("Provide at least a date or a mileage.")

        return cleaned_data


class PartForm(forms.ModelForm):
    """Provide a form for creating and updating vehicle parts."""

    class Meta:
        model = Part
        fields = (
            "name",
            "manufacturer",
            "part_number",
        )
