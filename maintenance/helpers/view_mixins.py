from django.db.models import QuerySet

from common.mixins import SubscriptionQuotaMixin
from maintenance.models import MaintenanceSchedule


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
