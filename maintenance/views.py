from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.urls import reverse_lazy
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
    SubscriptionQuotaMixin,
    UserFormKwargsMixin,
    VehicleCreateMixin,
    VehicleListMixin,
    VehicleOwnerMixin,
)
from maintenance.forms import MaintenanceScheduleForm, PartForm, ServiceRecordForm
from maintenance.models import MaintenanceSchedule, Part, ServiceRecord

# --------------------------- SERVICE RECORD ---------------------------


class ServiceRecordCreateView(
    LoginRequiredMixin,
    SubscriptionQuotaMixin,
    UserFormKwargsMixin,
    VehicleCreateMixin,
    CreateView,
):
    """Create a new service record for a selected vehicle."""

    form_class = ServiceRecordForm
    template_name = "maintenance/service_record_form.html"
    quota_resource = "service_records"

    def get_quota_queryset(self) -> QuerySet:
        """Return all service records owned by the current user."""

        return ServiceRecord.objects.filter(
            vehicle__owner=self.request.user,
        )


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
    LoginRequiredMixin,
    UserFormKwargsMixin,
    OwnedVehicleRecordMixin,
    RedirectToDetailMixin,
    UpdateView,
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


class MaintenanceScheduleCreateView(
    LoginRequiredMixin,
    SubscriptionQuotaMixin,
    UserFormKwargsMixin,
    VehicleCreateMixin,
    CreateView,
):
    """Create a maintenance schedule for a selected vehicle."""

    form_class = MaintenanceScheduleForm
    template_name = "maintenance/maintenance_schedule_form.html"
    quota_resource = "maintenance_schedules"

    def get_quota_queryset(self) -> QuerySet:
        """Returns all active maintenance schedules for the current user."""
        return MaintenanceSchedule.objects.filter(
            vehicle__owner=self.request.user,
            is_completed=False,
        )

    def should_check_quota(self, form) -> bool:
        """Check the quota only when creating an incomplete schedule."""

        is_completed = form.cleaned_data["is_completed"]

        return not is_completed


class MaintenanceScheduleListView(
    LoginRequiredMixin,
    VehicleListMixin,
    ListView,
):
    """List maintenance schedules for a selected vehicle."""

    model = MaintenanceSchedule
    template_name = "maintenance/maintenance_schedule_list.html"
    context_object_name = "maintenance_schedules"


class MaintenanceScheduleDetailView(
    LoginRequiredMixin,
    OwnedVehicleRecordMixin,
    DetailView,
):
    """Display the details of a maintenance schedule."""

    model = MaintenanceSchedule
    template_name = "maintenance/maintenance_schedule_detail.html"
    context_object_name = "maintenance_schedule"


class MaintenanceScheduleUpdateView(
    LoginRequiredMixin,
    SubscriptionQuotaMixin,
    UserFormKwargsMixin,
    RedirectToDetailMixin,
    OwnedVehicleRecordMixin,
    UpdateView,
):
    """Update an existing maintenance schedule."""

    model = MaintenanceSchedule
    form_class = MaintenanceScheduleForm
    template_name = "maintenance/maintenance_schedule_form.html"
    context_object_name = "maintenance_schedule"
    detail_url_name = "maintenance:maintenance-schedule-detail"
    quota_resource = "maintenance_schedules"

    def get_quota_queryset(self) -> QuerySet:
        return MaintenanceSchedule.objects.filter(
            vehicle__owner=self.request.user,
            is_completed=False,
        )

    def should_check_quota(self, form):
        """Check the quota when reopening a completed maintenance schedule."""

        was_completed = (
            MaintenanceSchedule.objects.filter(
                vehicle__owner=self.request.user,
            )
            .values_list("is_completed", flat=True)
            .get(
                pk=self.object.pk,
            )
        )

        is_completed = form.cleaned_data["is_completed"]

        return was_completed and not is_completed


class MaintenanceScheduleDeleteView(
    LoginRequiredMixin,
    RedirectToVehicleListMixin,
    OwnedVehicleRecordMixin,
    DeleteView,
):
    """Delete a maintenance schedule after confirmation."""

    model = MaintenanceSchedule
    template_name = "maintenance/maintenance_schedule_delete.html"
    context_object_name = "maintenance_schedule"
    vehicle_list_url_name = "maintenance:maintenance-schedule-list"


# --------------------------- PARTS ---------------------------


class PartCreateView(
    LoginRequiredMixin,
    SubscriptionQuotaMixin,
    CreateView,
):
    """Create a new part in the authenticated user's personal catalog."""

    model = Part
    form_class = PartForm
    template_name = "maintenance/part_form.html"
    success_url = reverse_lazy("maintenance:part-list")
    quota_resource = "parts"

    def get_quota_queryset(self) -> QuerySet:
        """Return all catalog parts owned by the current user."""

        return Part.objects.filter(
            owner=self.request.user,
        )

    def form_valid(self, form):
        """Assign the authenticated user as the part owner before saving."""

        form.instance.owner = self.request.user
        return super().form_valid(form)


class PartListView(LoginRequiredMixin, VehicleOwnerMixin, ListView):
    """List parts belonging to the authenticated user."""

    model = Part
    template_name = "maintenance/part_list.html"
    context_object_name = "parts"


class PartDetailView(LoginRequiredMixin, VehicleOwnerMixin, DetailView):
    """Display the details of an existing part."""

    model = Part
    template_name = "maintenance/part_detail.html"
    context_object_name = "part"


class PartUpdateView(
    LoginRequiredMixin,
    RedirectToDetailMixin,
    VehicleOwnerMixin,
    UpdateView,
):
    """Update an existing part."""

    model = Part
    form_class = PartForm
    template_name = "maintenance/part_form.html"
    context_object_name = "part"
    detail_url_name = "maintenance:part-detail"


class PartDeleteView(LoginRequiredMixin, VehicleOwnerMixin, DeleteView):
    """Delete an existing part."""

    model = Part
    template_name = "maintenance/part_confirm_delete.html"
    context_object_name = "part"
    success_url = reverse_lazy("maintenance:part-list")
