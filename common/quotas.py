from collections.abc import Mapping

from accounts.models import Account

SUBSCRIPTION_LIMITS: Mapping[str, Mapping[str, int | None]] = {
    "Free": {
        "vehicles": 1,
        "service_records": 15,
        "odometer_entries": 30,
        "maintenance_schedules": 0,
        "maintenance_items": 10,
        "documents": 2,
    },
    "VIP": {
        "vehicles": 10,
        "service_records": None,
        "odometer_entries": None,
        "maintenance_schedules": None,
        "maintenance_items": None,
        "documents": None,
    },
}


def get_subscription_plan(user: Account) -> str:
    """Determine the user's subscription plan based on group membership.

    Superusers are exempt from subscription restrictions. Users without
    VIP membership are treated as Free subscribers.
    """

    if user.is_superuser:
        return "Superuser"

    if user.groups.filter(name="VIP").exists():
        return "VIP"

    return "Free"


def get_subscription_limit(user: Account, resource: str) -> int | None:
    """Return the configured resource limit for the user's subscription plan.

    Return None when the resource is unlimited or the user is a superuser.
    Raise KeyError for an unknown resource on a restricted plan.
    """

    plan = get_subscription_plan(user)

    if plan == "Superuser":
        return None

    return SUBSCRIPTION_LIMITS[plan][resource]
