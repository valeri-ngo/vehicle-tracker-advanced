def get_vehicle_limit(user):
    """Return the vehicle quota for the user's subscription."""

    return get_subscription_limit(user, "vehicles")


SUBSCRIPTION_LIMITS = {
    "Free": {
        "vehicles": 1,
        "service_records": 15,
        "odometer_entries": 30,
        "maintenance_schedules": 2,
        "parts": 10,
        "documents": 2,
    },
    "VIP": {
        "vehicles": 10,
        "service_records": None,
        "odometer_entries": None,
        "maintenance_schedules": None,
        "parts": None,
        "documents": None,
    },
}


def get_subscription_plan(user):
    """Return the subscription plan of the given user."""

    if user.is_superuser:
        return "Superuser"

    if user.groups.filter(name="VIP").exists():
        return "VIP"

    return "Free"


def get_subscription_limit(user, resource):
    """Return the subscription limit for the specified resource."""

    plan = get_subscription_plan(user)

    if plan == "Superuser":
        return None

    return SUBSCRIPTION_LIMITS[plan][resource]
