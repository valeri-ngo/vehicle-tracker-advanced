from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import QuerySet
from django.forms.models import ModelForm
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django.views.generic.list import ListView

from common.mixins import OwnedObjectMixin, SubscriptionQuotaMixin, VehicleCreateMixin
from common.quotas import get_subscription_limit

from .forms import OdometerEntryForm, VehicleCreateForm, VehicleUpdateForm
from .models import OdometerEntry, Vehicle
from .validators import validate_odometer_entry

# ------------------------- VEHICLES -------------------------


class VehicleListView(
    LoginRequiredMixin,
    OwnedObjectMixin,
    ListView,
):
    """Display the vehicles registered to the current user.

    Restrict the queryset to owned vehicles to prevent access
    to records belonging to other accounts.
    """

    model = Vehicle
    template_name = "vehicles/vehicle_list.html"
    context_object_name = "vehicles"


class VehicleCreateView(
    LoginRequiredMixin,
    SubscriptionQuotaMixin,
    CreateView,
):
    """Handle vehicle registration within the user's subscription limits.

    Create the vehicle and its initial odometer reading within a single
    transaction to keep the mileage history consistent.
    """

    form_class = VehicleCreateForm
    template_name = "vehicles/vehicle_form.html"
    success_url = reverse_lazy("vehicles:vehicle-list")
    quota_resource = "vehicles"

    @staticmethod
    def _create_initial_odometer_entry(vehicle: Vehicle) -> None:
        """Initialize the vehicle's odometer history using its starting mileage."""

        OdometerEntry.objects.create(
            vehicle=vehicle,
            mileage=vehicle.current_mileage,
            recorded_at=vehicle.created_at,
        )

    def get_quota_queryset(self) -> QuerySet:
        """Return all vehicles owned by the current user."""

        return Vehicle.objects.filter(
            owner=self.request.user,
        )

    def get_quota_error(self) -> str | None:
        """Validate both vehicle and odometer subscription quotas."""

        error = super().get_quota_error()

        if error is not None:
            return error

        limit = get_subscription_limit(
            self.request.user,
            "odometer_entries",
        )

        if limit is None:
            return None

        count = OdometerEntry.objects.filter(
            vehicle__owner=self.request.user,
        ).count()

        if count >= limit:
            return "Your plan does not allow additional odometer entries."

        return None

    def form_valid(self, form: ModelForm) -> HttpResponse:
        """Create a vehicle and initial odometer entry within the subscription quota."""

        form.instance.owner = self.request.user

        with transaction.atomic():
            response = super().form_valid(form)

            if self.object is None:
                return response

            vehicle = self.object
            assert isinstance(vehicle, Vehicle)

            self._create_initial_odometer_entry(vehicle)

        return response


class VehicleDetailView(
    LoginRequiredMixin,
    OwnedObjectMixin,
    DetailView,
):
    """Display the details of a vehicle owned by the current user.

    Use the ownership-filtered queryset to prevent unauthorized access
    to vehicles registered by other accounts.
    """

    model = Vehicle
    template_name = "vehicles/vehicle_detail.html"
    context_object_name = "vehicle"


class VehicleUpdateView(
    LoginRequiredMixin,
    OwnedObjectMixin,
    UpdateView,
):
    """Update the details of a vehicle owned by the current user."""

    model = Vehicle
    form_class = VehicleUpdateForm
    template_name = "vehicles/vehicle_form.html"
    success_url = reverse_lazy("vehicles:vehicle-list")

    def form_valid(self, form: ModelForm) -> HttpResponseRedirect:
        """Persist only modified vehicle fields.

        Avoid overwriting mileage changes made by concurrent odometer
        entry operations.
        """

        self.object = form.save(commit=False)

        self.object.save(update_fields=form.changed_data)

        return HttpResponseRedirect(self.get_success_url())


class VehicleDeleteView(
    LoginRequiredMixin,
    OwnedObjectMixin,
    DeleteView,
):
    """Allow users to delete vehicles registered to their account.

    Related records are removed through the model's cascading
    foreign key relationships.
    """

    model = Vehicle
    template_name = "vehicles/vehicle_confirm_delete.html"
    context_object_name = "vehicle"
    success_url = reverse_lazy("vehicles:vehicle-list")


# ---------------------- ODOMETER ----------------------


class OdometerEntryCreateView(
    LoginRequiredMixin,
    SubscriptionQuotaMixin,
    VehicleCreateMixin,
    CreateView,
):
    """Handle odometer entry creation within subscription quotas."""

    form_class = OdometerEntryForm
    template_name = "vehicles/odometer_form.html"
    quota_resource = "odometer_entries"

    def get_quota_queryset(self) -> QuerySet:
        """Return all odometer entries owned by the current user."""

        return OdometerEntry.objects.filter(
            vehicle__owner=self.request.user,
        )

    def get_form_kwargs(self) -> dict[str, Any]:
        """Pass the selected vehicle to the odometer entry form."""

        kwargs = super().get_form_kwargs()
        kwargs["vehicle"] = self.vehicle
        return kwargs

    def validate_locked_form(self, form: ModelForm) -> bool:
        """Revalidate odometer entry consistency while holding the account lock."""

        self.vehicle.refresh_from_db(fields=["current_mileage"])

        mileage = form.cleaned_data["mileage"]
        recorded_at = form.cleaned_data["recorded_at"]

        errors = validate_odometer_entry(self.vehicle, mileage, recorded_at)

        for field, message in errors:
            form.add_error(field, message)

        return not errors

    def form_valid(self, form):
        """Save an odometer entry and update the vehicle's current mileage."""

        with transaction.atomic():
            response = super().form_valid(form)

            if self.object is None:
                return response

            entry = self.object
            assert isinstance(entry, OdometerEntry)

            self._update_vehicle_mileage(entry)

        return response

    def _update_vehicle_mileage(self, entry: OdometerEntry) -> None:
        """Update the vehicle's current mileage when a higher reading is recorded.

        Refresh the stored mileage before comparing values to ensure that
        historical readings do not reduce the vehicle's current mileage.
        """

        self.vehicle.refresh_from_db(fields=["current_mileage"])

        if entry.mileage > self.vehicle.current_mileage:
            self.vehicle.current_mileage = entry.mileage
            self.vehicle.save(update_fields=["current_mileage"])
