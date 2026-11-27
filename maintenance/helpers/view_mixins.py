from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.forms.models import ModelForm
from django.http import HttpResponse

from common.mixins import SubscriptionQuotaMixin
from maintenance.helpers.querysets import filter_available_maintenance_items
from maintenance.models import MaintenanceItem, MaintenanceSchedule


class MaintenanceScheduleQuotaMixin(SubscriptionQuotaMixin):
    """Apply subscription quotas to active maintenance schedules.

    Count incomplete schedules across all vehicles owned by the
    current user.
    """

    quota_resource = "maintenance_schedules"

    def get_quota_queryset(self) -> QuerySet:
        """Apply subscription quotas to active maintenance schedules.

        Count incomplete schedules across all vehicles owned by the
        current user.
        """

        return MaintenanceSchedule.objects.filter(
            vehicle__owner=self.request.user,
            is_completed=False,
        )


class AvailableMaintenanceItemsMixin:
    """Provide read access to predefined and user-owned maintenance items.

    Prevent users from accessing custom maintenance items owned by
    other users.
    """

    def get_queryset(self) -> QuerySet[MaintenanceItem]:
        """Return maintenance items available to the authenticated user."""

        queryset = super().get_queryset()

        return filter_available_maintenance_items(queryset, self.request.user)


class MaintenanceItemIntegrityMixin:
    """Handle maintenance item uniqueness conflicts during persistence."""

    def form_valid(self, form: ModelForm) -> HttpResponse:
        """Save the maintenance item and handle concurrent duplicate name conflicts."""

        try:
            with transaction.atomic():
                return super().form_valid(form)

        except IntegrityError as error:
            diag = getattr(error.__cause__, "diag", None)

            constraint_name = getattr(diag, "constraint_name", None)

            if constraint_name == "unique_custom_maintenance_item_per_owner":
                form.add_error(
                    "name",
                    "A maintenance item with this name already exists in your checklist.",
                )
                return self.form_invalid(form)

            raise


class MaintenanceItemProtectionMixin:
    """Prevent modification and deletion of maintenance items in use."""

    def get_object(self, queryset=None) -> MaintenanceItem:
        """Retrieve the maintenance item and prevent changes while it is in use."""

        maintenance_item: MaintenanceItem = super().get_object(queryset)

        if maintenance_item.is_in_use():
            raise PermissionDenied(
                "Maintenance items in use cannot be modified or deleted."
            )

        return maintenance_item
