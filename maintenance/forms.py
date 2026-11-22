from typing import ClassVar

from django import forms
from django.utils import timezone

from maintenance.models import MaintenanceSchedule, ServiceRecord


class ServiceRecordForm(forms.ModelForm):
    class Meta:
        model = ServiceRecord
        fields = (
            "service_type",
            "description",
            "mileage",
            "service_date",
            "cost",
        )
        widgets: ClassVar[dict[str, forms.DateInput]] = {
            "service_date": forms.DateInput(
                attrs={
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
        }

    def clean_service_date(self):
        service_date = self.cleaned_data["service_date"]

        if service_date > timezone.localdate():
            raise forms.ValidationError("Service date cannot be in the future.")

        return service_date


class MaintenanceScheduleForm(forms.ModelForm):
    class Meta:
        model = MaintenanceSchedule
        fields = (
            "service_type",
            "description",
            "due_date",
            "due_mileage",
            "is_completed",
        )
        widgets: ClassVar[dict[str, forms.DateInput]] = {
            "due_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        due_date = cleaned_data.get("due_date")
        due_mileage = cleaned_data.get("due_mileage")

        if not due_date and due_mileage is None:
            raise forms.ValidationError("Provide at least a date or a mileage.")

        return cleaned_data
