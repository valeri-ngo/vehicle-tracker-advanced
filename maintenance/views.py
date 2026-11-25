from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.forms.models import ModelForm
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from common.mixins import (
    OwnedObjectMixin,
    OwnedVehicleRecordMixin,
    RedirectToDetailMixin,
    RedirectToVehicleListMixin,
    SubscriptionQuotaMixin,
    UserFormKwargsMixin,
    VehicleCreateMixin,
    VehicleListMixin,
)
from maintenance.forms import MaintenanceScheduleForm, PartForm, ServiceRecordForm
from maintenance.helpers.view_mixins import MaintenanceScheduleQuotaMixin
from maintenance.models import MaintenanceSchedule, Part, ServiceRecord

# --------------------------- SERVICE RECORD ---------------------------


class ServiceRecordCreateView(
    LoginRequiredMixin,
    SubscriptionQuotaMixin,
    UserFormKwargsMixin,
    VehicleCreateMixin,
    CreateView,
):
    """Handle part creation within the user's personal catalog.

    Enforce subscription limits and assign ownership to the
    authenticated user.
    """

    form_class = ServiceRecordForm
    template_name = "maintenance/service_record_form.html"
    quota_resource = "service_records"

    def get_quota_queryset(self) -> QuerySet[ServiceRecord]:
        """Return all service records owned by the current user."""

        return ServiceRecord.objects.filter(
            vehicle__owner=self.request.user,
        )


class ServiceRecordListView(
    LoginRequiredMixin,
    VehicleListMixin,
    ListView,
):
    """List service records for a vehicle owned by the current user."""

    model = ServiceRecord
    template_name = "maintenance/service_record_list.html"
    context_object_name = "service_records"


class ServiceRecordDetailView(LoginRequiredMixin, OwnedVehicleRecordMixin, DetailView):
    """Display an existing service record with ownership restrictions."""

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
    """Update a service record owned by the current user.

    Restrict part selection to the user's personal catalog.
    """

    model = ServiceRecord
    form_class = ServiceRecordForm
    template_name = "maintenance/service_record_form.html"
    context_object_name = "service_record"
    detail_url_name = "maintenance:service-record-detail"


class ServiceRecordDeleteView(
    LoginRequiredMixin, RedirectToVehicleListMixin, OwnedVehicleRecordMixin, DeleteView
):
    """Delete an owned service record after user confirmation."""

    model = ServiceRecord
    template_name = "maintenance/service_record_delete.html"
    context_object_name = "service_record"
    vehicle_list_url_name = "maintenance:service-record-list"


# --------------------------- MAINTENANCE SCHEDULE ---------------------------


class MaintenanceScheduleCreateView(
    LoginRequiredMixin,
    MaintenanceScheduleQuotaMixin,
    UserFormKwargsMixin,
    VehicleCreateMixin,
    CreateView,
):
    """Create a maintenance schedule for a vehicle owned by the user.

    Enforce subscription limits only when creating an incomplete
    maintenance schedule.
    """

    form_class = MaintenanceScheduleForm
    template_name = "maintenance/maintenance_schedule_form.html"

    def should_check_quota(self, form: ModelForm) -> bool:
        """Check the quota only when creating an incomplete schedule."""

        is_completed = form.cleaned_data["is_completed"]

        return not is_completed


class MaintenanceScheduleListView(
    LoginRequiredMixin,
    VehicleListMixin,
    ListView,
):
    """List maintenance schedules for a vehicle owned by the current user."""

    model = MaintenanceSchedule
    template_name = "maintenance/maintenance_schedule_list.html"
    context_object_name = "maintenance_schedules"


class MaintenanceScheduleDetailView(
    LoginRequiredMixin,
    OwnedVehicleRecordMixin,
    DetailView,
):
    """Display the details of a maintenance schedule owned by the current user."""

    model = MaintenanceSchedule
    template_name = "maintenance/maintenance_schedule_detail.html"
    context_object_name = "maintenance_schedule"


class MaintenanceScheduleUpdateView(
    LoginRequiredMixin,
    MaintenanceScheduleQuotaMixin,
    UserFormKwargsMixin,
    RedirectToDetailMixin,
    OwnedVehicleRecordMixin,
    UpdateView,
):
    """Update a maintenance schedule owned by the current user.

    Enforce subscription limits when reopening a previously completed
    maintenance schedule.
    """

    model = MaintenanceSchedule
    form_class = MaintenanceScheduleForm
    template_name = "maintenance/maintenance_schedule_form.html"
    context_object_name = "maintenance_schedule"
    detail_url_name = "maintenance:maintenance-schedule-detail"

    def should_check_quota(self, form: ModelForm) -> bool:
        """Check the quota when reopening a completed maintenance schedule."""

        was_completed = self._was_completed()
        is_completed = form.cleaned_data["is_completed"]

        return was_completed and not is_completed

    def _was_completed(self) -> bool:
        """Retrieve the schedule's completion status from the database."""

        was_completed = (
            MaintenanceSchedule.objects.filter(
                vehicle__owner=self.request.user,
            )
            .values_list("is_completed", flat=True)
            .get(
                pk=self.object.pk,
            )
        )

        return was_completed


class MaintenanceScheduleDeleteView(
    LoginRequiredMixin,
    RedirectToVehicleListMixin,
    OwnedVehicleRecordMixin,
    DeleteView,
):
    """Delete an owned maintenance schedule after user confirmation."""

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
    """Handle part creation within the user's personal catalog.

    Enforce subscription limits and assign ownership to the
    authenticated user.
    """

    model = Part
    form_class = PartForm
    template_name = "maintenance/part_form.html"
    success_url = reverse_lazy("maintenance:part-list")
    quota_resource = "parts"

    def get_quota_queryset(self) -> QuerySet[Part]:
        """Return all catalog parts owned by the current user."""

        return Part.objects.filter(
            owner=self.request.user,
        )

    def form_valid(self, form: ModelForm) -> HttpResponse:
        """Assign the authenticated user as the part owner before saving."""

        form.instance.owner = self.request.user
        return super().form_valid(form)


class PartListView(LoginRequiredMixin, OwnedObjectMixin, ListView):
    """List parts belonging to the authenticated user."""

    model = Part
    template_name = "maintenance/part_list.html"
    context_object_name = "parts"


class PartDetailView(LoginRequiredMixin, OwnedObjectMixin, DetailView):
    """Display the details of a part owned by the current user."""

    model = Part
    template_name = "maintenance/part_detail.html"
    context_object_name = "part"


class PartUpdateView(
    LoginRequiredMixin,
    RedirectToDetailMixin,
    OwnedObjectMixin,
    UpdateView,
):
    """Update a part in the current user's personal catalog."""

    model = Part
    form_class = PartForm
    template_name = "maintenance/part_form.html"
    context_object_name = "part"
    detail_url_name = "maintenance:part-detail"


class PartDeleteView(LoginRequiredMixin, OwnedObjectMixin, DeleteView):
    """Remove a part from the user's personal catalog after confirmation."""

    model = Part
    template_name = "maintenance/part_confirm_delete.html"
    context_object_name = "part"
    success_url = reverse_lazy("maintenance:part-list")
