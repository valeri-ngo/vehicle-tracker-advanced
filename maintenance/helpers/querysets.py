from django.db.models import Q, QuerySet

from accounts.models import Account
from maintenance.models import MaintenanceItem


def filter_available_maintenance_items(
    queryset: QuerySet[MaintenanceItem],
    user: Account,
) -> QuerySet[MaintenanceItem]:
    """Filter maintenance items to predefined and user-owned entries.

    Exclude custom maintenance items belonging to other users.
    """

    return queryset.filter(Q(owner__isnull=True) | Q(owner=user))
