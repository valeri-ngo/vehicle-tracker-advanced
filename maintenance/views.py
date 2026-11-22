from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from common.mixins import (
    OwnedVehicleRecordMixin,
    RedirectToDetailMixin,
    RedirectToVehicleListMixin,
    VehicleCreateMixin,
    VehicleListMixin,
    VehicleOwnerMixin,
)
from maintenance.forms import MaintenanceScheduleForm, PartForm, ServiceRecordForm
from maintenance.models import MaintenanceSchedule, Part, ServiceRecord

# --------------------------- SERVICE RECORD ---------------------------


class ServiceRecordCreateView(LoginRequiredMixin, VehicleCreateMixin, CreateView):
    """Create a new service record for a selected vehicle."""

    form_class = ServiceRecordForm
    template_name = "maintenance/service_record_form.html"


class ServiceRecordListView(LoginRequiredMixin, VehicleListMixin, ListView):
    """List service records for a selected vehicle."""

    model = ServiceRecord
    template_name = "maintenance/service_record_list.html"
    context_object_name = "service_records"


class ServiceRecordDetailView(LoginRequiredMixin, OwnedVehicleRecordMixin, DetailView):
    """Display the details of an existing service record."""

    model = ServiceRecord
    template_name = "maintenance/service_record_detail.html"
    context_object_name = "service_record"


class ServiceRecordUpdateView(
    LoginRequiredMixin, RedirectToDetailMixin, OwnedVehicleRecordMixin, UpdateView
):
    """Update an existing service record."""

    model = ServiceRecord
    form_class = ServiceRecordForm
    template_name = "maintenance/service_record_form.html"
    context_object_name = "service_record"
    detail_url_name = "maintenance:service-record-detail"


class ServiceRecordDeleteView(
    LoginRequiredMixin, RedirectToVehicleListMixin, OwnedVehicleRecordMixin, DeleteView
):
    """Delete an existing service record after confirmation."""

    model = ServiceRecord
    template_name = "maintenance/service_record_delete.html"
    context_object_name = "service_record"
    vehicle_list_url_name = "maintenance:service-record-list"


# --------------------------- MAINTENANCE SCHEDULE ---------------------------


class MaintenanceScheduleCreateView(LoginRequiredMixin, VehicleCreateMixin, CreateView):
    """Create a maintenance schedule for a selected vehicle."""

    form_class = MaintenanceScheduleForm
    template_name = "maintenance/maintenance_schedule_form.html"


class MaintenanceScheduleListView(LoginRequiredMixin, VehicleListMixin, ListView):
    """List maintenance schedules for a selected vehicle."""

    model = MaintenanceSchedule
    template_name = "maintenance/maintenance_schedule_list.html"
    context_object_name = "maintenance_schedules"


class MaintenanceScheduleDetailView(
    LoginRequiredMixin, OwnedVehicleRecordMixin, DetailView
):
    """Display the details of a maintenance schedule."""

    model = MaintenanceSchedule
    template_name = "maintenance/maintenance_schedule_detail.html"
    context_object_name = "maintenance_schedule"


class MaintenanceScheduleUpdateView(
    LoginRequiredMixin, RedirectToDetailMixin, OwnedVehicleRecordMixin, UpdateView
):
    """Update an existing maintenance schedule."""

    model = MaintenanceSchedule
    form_class = MaintenanceScheduleForm
    template_name = "maintenance/maintenance_schedule_form.html"
    context_object_name = "maintenance_schedule"
    detail_url_name = "maintenance:maintenance-schedule-detail"


class MaintenanceScheduleDeleteView(
    LoginRequiredMixin, RedirectToVehicleListMixin, OwnedVehicleRecordMixin, DeleteView
):
    """Delete a maintenance schedule after confirmation."""

    model = MaintenanceSchedule
    template_name = "maintenance/maintenance_schedule_delete.html"
    context_object_name = "maintenance_schedule"
    vehicle_list_url_name = "maintenance:maintenance-schedule-list"


# --------------------------- PARTS ---------------------------


class PartCreateView(LoginRequiredMixin, CreateView):
    """Create a new part in the authenticated user's personal catalog."""

    model = Part
    form_class = PartForm

    def form_valid(self, form):
        """Assign the authenticated user as the part owner before saving."""

        form.instance.owner = self.request.user
        return super().form_valid(form)


class PartListView(LoginRequiredMixin, VehicleOwnerMixin, ListView):
    """List parts belonging to the authenticated user."""

    model = Part
    template_name = "maintenance/part_list.html"
    context_object_name = "parts"
