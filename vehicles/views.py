from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django.views.generic.list import ListView

from common.mixins import VehicleCreateMixin, VehicleOwnerMixin

from .forms import OdometerEntryForm, VehicleCreateForm, VehicleUpdateForm
from .models import OdometerEntry, Vehicle

# ------------------------- VEHICLES -------------------------


class VehicleListView(LoginRequiredMixin, VehicleOwnerMixin, ListView):
    model = Vehicle
    template_name = "vehicles/vehicle_list.html"
    context_object_name = "vehicles"


class VehicleCreateView(LoginRequiredMixin, CreateView):
    form_class = VehicleCreateForm
    template_name = "vehicles/vehicle_form.html"
    success_url = reverse_lazy("vehicles:vehicle-list")

    def form_valid(self, form):
        form.instance.owner = self.request.user

        with transaction.atomic():
            response = super().form_valid(form)

            vehicle = self.object
            assert isinstance(vehicle, Vehicle)

            OdometerEntry.objects.create(
                vehicle=vehicle,
                mileage=vehicle.current_mileage,
                recorded_at=vehicle.created_at,
            )

        return response


class VehicleDetailView(LoginRequiredMixin, VehicleOwnerMixin, DetailView):
    model = Vehicle
    template_name = "vehicles/vehicle_detail.html"
    context_object_name = "vehicle"


class VehicleUpdateView(LoginRequiredMixin, VehicleOwnerMixin, UpdateView):
    model = Vehicle
    form_class = VehicleUpdateForm
    template_name = "vehicles/vehicle_form.html"
    success_url = reverse_lazy("vehicles:vehicle-list")


class VehicleDeleteView(LoginRequiredMixin, VehicleOwnerMixin, DeleteView):
    model = Vehicle
    template_name = "vehicles/vehicle_confirm_delete.html"
    context_object_name = "vehicle"
    success_url = reverse_lazy("vehicles:vehicle-list")


# ---------------------- ODOMETER ----------------------


class OdometerEntryCreateView(LoginRequiredMixin, VehicleCreateMixin, CreateView):
    form_class = OdometerEntryForm
    template_name = "vehicles/odometer_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["vehicle"] = self.vehicle
        return kwargs

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)

            entry = self.object
            assert isinstance(entry, OdometerEntry)

            if entry.mileage > self.vehicle.current_mileage:
                self.vehicle.current_mileage = entry.mileage
                self.vehicle.save(update_fields=["current_mileage"])

        return response
