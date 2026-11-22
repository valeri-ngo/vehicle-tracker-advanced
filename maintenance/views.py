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
)
from maintenance.forms import MaintenanceScheduleForm, ServiceRecordForm
from maintenance.models import MaintenanceSchedule, ServiceRecord

# --------------------------- SERVICE RECORD ---------------------------------


class ServiceRecordCreateView(LoginRequiredMixin, VehicleCreateMixin, CreateView):
    form_class = ServiceRecordForm
    template_name = "maintenance/service_record_form.html"


class ServiceRecordListView(LoginRequiredMixin, VehicleListMixin, ListView):
    model = ServiceRecord
    template_name = "maintenance/service_record_list.html"
    context_object_name = "service_records"


class ServiceRecordDetailView(LoginRequiredMixin, OwnedVehicleRecordMixin, DetailView):
    model = ServiceRecord
    template_name = "maintenance/service_record_detail.html"
    context_object_name = "service_record"


class ServiceRecordUpdateView(
    LoginRequiredMixin, RedirectToDetailMixin, OwnedVehicleRecordMixin, UpdateView
):
    model = ServiceRecord
    form_class = ServiceRecordForm
    template_name = "maintenance/service_record_form.html"
    context_object_name = "service_record"
    detail_url_name = "maintenance:service-record-detail"


class ServiceRecordDeleteView(
    LoginRequiredMixin, RedirectToVehicleListMixin, OwnedVehicleRecordMixin, DeleteView
):
    model = ServiceRecord
    template_name = "maintenance/service_record_delete.html"
    context_object_name = "service_record"
    vehicle_list_url_name = "maintenance:service-record-list"


# -------------------------- MAINTENANCE SCHEDULE ----------------------------------


class MaintenanceScheduleCreateView(LoginRequiredMixin, VehicleCreateMixin, CreateView):
    form_class = MaintenanceScheduleForm
    template_name = "maintenance/maintenance_schedule_form.html"


class MaintenanceScheduleListView(LoginRequiredMixin, VehicleListMixin, ListView):
    model = MaintenanceSchedule
    template_name = "maintenance/maintenance_schedule_list.html"
    context_object_name = "maintenance_schedules"


class MaintenanceScheduleDetailView(
    LoginRequiredMixin, OwnedVehicleRecordMixin, DetailView
):
    model = MaintenanceSchedule
    template_name = "maintenance/maintenance_schedule_detail.html"
    context_object_name = "maintenance_schedule"


class MaintenanceScheduleUpdateView(
    LoginRequiredMixin, RedirectToDetailMixin, OwnedVehicleRecordMixin, UpdateView
):
    model = MaintenanceSchedule
    form_class = MaintenanceScheduleForm
    template_name = "maintenance/maintenance_schedule_form.html"
    context_object_name = "maintenance_schedule"
    detail_url_name = "maintenance:maintenance-schedule-detail"


class MaintenanceScheduleDeleteView(
    LoginRequiredMixin, RedirectToVehicleListMixin, OwnedVehicleRecordMixin, DeleteView
):
    model = MaintenanceSchedule
    template_name = "maintenance/maintenance_schedule_delete.html"
    context_object_name = "maintenance_schedule"
    vehicle_list_url_name = "maintenance:maintenance-schedule-list"
