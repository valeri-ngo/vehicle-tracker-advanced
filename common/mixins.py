from django.shortcuts import get_object_or_404
from django.urls import reverse

from vehicles.models import Vehicle


class VehicleScopedMixin:
    """Find a vehicle owned by the logged user."""

    vehicle: Vehicle

    def dispatch(self, request, *args, **kwargs):
        self.vehicle = get_object_or_404(
            Vehicle,
            pk=kwargs["pk"],
            owner_id=request.user.pk,
        )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vehicle"] = self.vehicle
        return context


class VehicleCreateMixin(VehicleScopedMixin):
    """Assign the selected vehicle to a new record."""

    def form_valid(self, form):
        form.instance.vehicle = self.vehicle
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "vehicles:vehicle-detail",
            kwargs={"pk": self.vehicle.pk},
        )


class VehicleListMixin(VehicleScopedMixin):
    """Shows records belonging to one owned vehicle."""

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                vehicle=self.vehicle,
            )
        )


class OwnedVehicleRecordMixin:
    """Restrict record access to the vehicle's owner."""

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                vehicle__owner_id=self.request.user.pk,
            )
            .select_related("vehicle")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vehicle"] = self.object.vehicle
        return context


class RedirectToDetailMixin:
    """Redirects to the record's detail page."""

    detail_url_name: str

    def get_success_url(self):
        return reverse(
            self.detail_url_name,
            kwargs={"pk": self.object.pk},
        )


class RedirectToVehicleListMixin:
    """Redirect to the related vehicle's record list."""

    vehicle_list_url_name: str

    def get_success_url(self):
        return reverse(
            self.vehicle_list_url_name,
            kwargs={"pk": self.object.vehicle_id},
        )


class VehicleOwnerMixin:
    """Restrict record access to the vehicle's owner."""

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                owner_id=self.request.user.pk,
            )
        )
