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
from maintenance.forms import (
    MaintenanceItemForm,
    MaintenanceScheduleForm,
    ServiceRecordForm,
)
from maintenance.helpers.view_mixins import (
    AvailableMaintenanceItemsMixin,
    MaintenanceItemIntegrityMixin,
    MaintenanceItemProtectionMixin,
    MaintenanceScheduleQuotaMixin,
)
from maintenance.models import MaintenanceItem, MaintenanceSchedule, ServiceRecord

# --------------------------- SERVICE RECORD ---------------------------


class ServiceRecordCreateView(
    LoginRequiredMixin,
    SubscriptionQuotaMixin,
    UserFormKwargsMixin,
    VehicleCreateMixin,
    CreateView,
):
    """Create a service record for a vehicle owned by the authenticated user.

    Enforce subscription limits and restrict maintenance item selection
    to predefined and user-owned items.
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

    Restrict maintenance item selection to predefined and user-owned items.
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


# --------------------------- MAINTENANCE ITEMS ---------------------------


class MaintenanceItemCreateView(
    LoginRequiredMixin,
    MaintenanceItemIntegrityMixin,
    SubscriptionQuotaMixin,
    UserFormKwargsMixin,
    CreateView,
):
    """Create a custom maintenance item for the authenticated user.

    Enforce subscription limits and assign ownership before saving.
    """

    model = MaintenanceItem
    form_class = MaintenanceItemForm
    template_name = "maintenance/maintenance_item_form.html"
    success_url = reverse_lazy("maintenance:maintenance-item-list")
    quota_resource = "maintenance_items"

    def get_quota_queryset(self) -> QuerySet[MaintenanceItem]:
        """Return custom maintenance items owned by the current user."""

        return MaintenanceItem.objects.filter(
            owner=self.request.user,
        )

    def form_valid(self, form: ModelForm) -> HttpResponse:
        """Assign ownership to the authenticated user before saving."""

        form.instance.owner = self.request.user
        return super().form_valid(form)


class MaintenanceItemListView(
    LoginRequiredMixin,
    AvailableMaintenanceItemsMixin,
    ListView,
):
    """List predefined and custom maintenance items available to the user."""

    model = MaintenanceItem
    template_name = "maintenance/maintenance_item_list.html"
    context_object_name = "maintenance_items"


class MaintenanceItemDetailView(
    LoginRequiredMixin,
    AvailableMaintenanceItemsMixin,
    DetailView,
):
    """Display a predefined or user-owned maintenance item."""

    model = MaintenanceItem
    template_name = "maintenance/maintenance_item_detail.html"
    context_object_name = "maintenance_item"


class MaintenanceItemUpdateView(
    LoginRequiredMixin,
    RedirectToDetailMixin,
    MaintenanceItemProtectionMixin,
    OwnedObjectMixin,
    UserFormKwargsMixin,
    MaintenanceItemIntegrityMixin,
    UpdateView,
):
    """Update an unused custom maintenance item owned by the current user."""

    model = MaintenanceItem
    form_class = MaintenanceItemForm
    template_name = "maintenance/maintenance_item_form.html"
    context_object_name = "maintenance_item"
    detail_url_name = "maintenance:maintenance-item-detail"


class MaintenanceItemDeleteView(
    LoginRequiredMixin,
    MaintenanceItemProtectionMixin,
    OwnedObjectMixin,
    DeleteView,
):
    """Delete an unused custom maintenance item owned by the current user."""

    model = MaintenanceItem
    template_name = "maintenance/maintenance_item_confirm_delete.html"
    context_object_name = "maintenance_item"
    success_url = reverse_lazy("maintenance:maintenance-item-list")
