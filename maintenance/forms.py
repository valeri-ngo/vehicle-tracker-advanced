from datetime import date
from typing import Any, ClassVar

from django import forms
from django.utils import timezone

from accounts.models import Account
from maintenance.helpers.form_mixins import MaintenanceItemQuerysetMixin
from maintenance.models import MaintenanceItem, MaintenanceSchedule, ServiceRecord


class ServiceRecordForm(MaintenanceItemQuerysetMixin, forms.ModelForm):
    """Handle the creation and editing of vehicle service records.

    Restrict maintenance item selection to predefined and user-owned items
    and prevent service records from being dated in the future.
    """

    class Meta:
        model = ServiceRecord
        fields = (
            "service_type",
            "description",
            "mileage",
            "service_date",
            "cost",
            "maintenance_items",
        )
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "service_date": forms.DateInput(
                attrs={
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
            "maintenance_items": forms.CheckboxSelectMultiple(),
        }

    def clean_service_date(self) -> date:
        """Ensure the service date is not in the future."""

        service_date = self.cleaned_data["service_date"]

        if service_date > timezone.localdate():
            raise forms.ValidationError("Service date cannot be in the future.")

        return service_date


class MaintenanceScheduleForm(MaintenanceItemQuerysetMixin, forms.ModelForm):
    """Handle the creation and editing of vehicle maintenance schedules.

    Require a due date, due mileage or both, and restrict maintenance item
    selection to predefined and user-owned items.
    """

    class Meta:
        model = MaintenanceSchedule
        fields = (
            "service_type",
            "description",
            "due_date",
            "due_mileage",
            "is_completed",
            "maintenance_items",
        )

        widgets: ClassVar[dict[str, forms.Widget]] = {
            "due_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "maintenance_items": forms.CheckboxSelectMultiple(),
        }

    def clean(self) -> dict[str, Any]:
        """Require at least a due date or a due mileage."""

        cleaned_data = super().clean() or self.cleaned_data

        due_date = cleaned_data.get("due_date")
        due_mileage = cleaned_data.get("due_mileage")

        if due_date is None and due_mileage is None:
            raise forms.ValidationError("Provide at least a date or a mileage.")

        return cleaned_data


class MaintenanceItemForm(forms.ModelForm):
    """Handle the creation and editing of custom maintenance items.

    Allow users to extend the predefined maintenance checklist with
    their own maintenance operations.
    """

    def __init__(
        self,
        *args: Any,
        user: Account,
        **kwargs: Any,
    ) -> None:
        """Initialize the form with the user responsible for the maintenance item."""

        super().__init__(*args, **kwargs)

        self.user = user

    def clean_name(self) -> str:
        """Validate the maintenance item name for uniqueness within the user's checklist.

        Exclude the current instance when updating an existing item.
        """

        name = self.cleaned_data["name"]

        queryset = MaintenanceItem.objects.filter(
            owner=self.user,
            name__iexact=name,
        )

        if self.instance.pk is not None:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError(
                "A maintenance item with this name already exists in your checklist."
            )

        return name

    class Meta:
        model = MaintenanceItem
        fields = ("name", "category")
