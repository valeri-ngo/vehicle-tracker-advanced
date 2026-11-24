from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import QuerySet
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django.views.generic.list import ListView

from common.mixins import SubscriptionQuotaMixin, VehicleCreateMixin, VehicleOwnerMixin
from common.quotas import get_subscription_limit

from .forms import OdometerEntryForm, VehicleCreateForm, VehicleUpdateForm
from .models import OdometerEntry, Vehicle
from .validators import validate_odometer_entry

# ------------------------- VEHICLES -------------------------


class VehicleListView(
    LoginRequiredMixin,
    VehicleOwnerMixin,
    ListView,
):
    model = Vehicle
    template_name = "vehicles/vehicle_list.html"
    context_object_name = "vehicles"


class VehicleCreateView(
    LoginRequiredMixin,
    SubscriptionQuotaMixin,
    CreateView,
):
    """Handle vehicle creation within subscription quotas."""

    form_class = VehicleCreateForm
    template_name = "vehicles/vehicle_form.html"
    success_url = reverse_lazy("vehicles:vehicle-list")
    quota_resource = "vehicles"

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

    def form_valid(self, form):
        """Create a vehicle and initial odometer entry within the subscription quota."""

        form.instance.owner = self.request.user

        with transaction.atomic():
            response = super().form_valid(form)

            if self.object is None:
                return response

            vehicle = self.object
            assert isinstance(vehicle, Vehicle)

            OdometerEntry.objects.create(
                vehicle=vehicle,
                mileage=vehicle.current_mileage,
                recorded_at=vehicle.created_at,
            )

        return response


class VehicleDetailView(
    LoginRequiredMixin,
    VehicleOwnerMixin,
    DetailView,
):
    model = Vehicle
    template_name = "vehicles/vehicle_detail.html"
    context_object_name = "vehicle"


class VehicleUpdateView(
    LoginRequiredMixin,
    VehicleOwnerMixin,
    UpdateView,
):
    """Update the details of a vehicle owned by the current user."""

    model = Vehicle
    form_class = VehicleUpdateForm
    template_name = "vehicles/vehicle_form.html"
    success_url = reverse_lazy("vehicles:vehicle-list")

    def form_valid(self, form):
        """Update vehicle details without overwriting the current mileage."""

        self.object = form.save(commit=False)

        self.object.save(update_fields=form.changed_data)

        return HttpResponseRedirect(self.get_success_url())


class VehicleDeleteView(
    LoginRequiredMixin,
    VehicleOwnerMixin,
    DeleteView,
):
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

    def get_form_kwargs(self):
        """Pass the selected vehicle to the odometer entry form."""

        kwargs = super().get_form_kwargs()
        kwargs["vehicle"] = self.vehicle
        return kwargs

    def validate_locked_form(self, form) -> bool:
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

            self.vehicle.refresh_from_db(fields=["current_mileage"])

            if entry.mileage > self.vehicle.current_mileage:
                self.vehicle.current_mileage = entry.mileage
                self.vehicle.save(update_fields=["current_mileage"])

        return response
