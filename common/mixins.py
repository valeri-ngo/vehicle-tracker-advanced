from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse

from common.quotas import get_subscription_limit
from vehicles.models import Vehicle


class VehicleScopedMixin:
    """Find a vehicle owned by the logged user."""

    vehicle: Vehicle

    def dispatch(self, request, *args, **kwargs):
        """Resolve the requested vehicle and verify ownership before handling the request."""

        self.vehicle = get_object_or_404(
            Vehicle,
            pk=kwargs["pk"],
            owner_id=request.user.pk,
        )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Include the selected vehicle in the template context."""

        context = super().get_context_data(**kwargs)
        context["vehicle"] = self.vehicle
        return context


class VehicleCreateMixin(VehicleScopedMixin):
    """Assign the selected vehicle to a new record."""

    def form_valid(self, form):
        """Assign the selected vehicle before saving the new record."""

        form.instance.vehicle = self.vehicle
        return super().form_valid(form)

    def get_success_url(self):
        """Return the selected vehicle's detail page URL."""

        return reverse(
            "vehicles:vehicle-detail",
            kwargs={"pk": self.vehicle.pk},
        )


class VehicleListMixin(VehicleScopedMixin):
    """Shows records belonging to one owned vehicle."""

    def get_queryset(self):
        """Return records associated with the selected vehicle."""

        return (
            super()
            .get_queryset()
            .filter(
                vehicle=self.vehicle,
            )
        )


class OwnedVehicleRecordMixin:
    """Restrict record access to the vehicle's owner."""

    request: HttpRequest

    def get_queryset(self):
        """Return records belonging to vehicles owned by the current user."""

        return (
            super()
            .get_queryset()
            .filter(
                vehicle__owner_id=self.request.user.pk,
            )
            .select_related("vehicle")
        )

    def get_context_data(self, **kwargs):
        """Include the record's associated vehicle in the template context."""

        context = super().get_context_data(**kwargs)
        context["vehicle"] = self.object.vehicle
        return context


class RedirectToDetailMixin:
    """Redirects to the record's detail page."""

    detail_url_name: str

    def get_success_url(self):
        """Return the detail page URL for the current record."""

        return reverse(
            self.detail_url_name,
            kwargs={"pk": self.object.pk},
        )


class RedirectToVehicleListMixin:
    """Redirect to the related vehicle's record list."""

    vehicle_list_url_name: str

    def get_success_url(self):
        """Return the related vehicle's record list URL."""

        return reverse(
            self.vehicle_list_url_name,
            kwargs={"pk": self.object.vehicle_id},
        )


class VehicleOwnerMixin:
    """Restrict record access to the vehicle's owner."""

    request: HttpRequest

    def get_queryset(self):
        """Return only vehicles owned by the current user."""

        return (
            super()
            .get_queryset()
            .filter(
                owner_id=self.request.user.pk,
            )
        )


class UserFormKwargsMixin:
    """Pass the authenticated user to Django model forms."""

    request: HttpRequest

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""

        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user

        return kwargs


class SubscriptionQuotaMixin:
    """Enforce subscription quotas for resource creation."""

    request: HttpRequest
    quota_resource: str | None = None

    def get_quota_queryset(self) -> QuerySet:
        """Return the queryset used to calculate resource usage."""

        raise NotImplementedError

    def get_quota_limit(self) -> int | None:
        """Return the subscription limit for the configured resource."""

        if self.quota_resource is None:
            raise NotImplementedError("quota_resource must be configured.")

        return get_subscription_limit(self.request.user, self.quota_resource)

    def is_quota_exceeded(self) -> bool:
        """Check whether the user has reached the subscription quota."""

        limit = self.get_quota_limit()

        if limit is None:
            return False

        count = self.get_quota_queryset().count()

        return count >= limit

    def should_check_quota(self, form):
        """Determine whether the submitted form requires a quota check."""

        return True

    def validate_locked_form(self, form) -> bool:
        """Validate additional business rules while holding the account lock."""

        return True

    def form_valid(self, form):
        """Validate quotas and business rules before saving a resource."""

        with transaction.atomic():
            User = get_user_model()

            User.objects.select_for_update().get(
                pk=self.request.user.pk,
            )

            if self.should_check_quota(form):
                error = self.get_quota_error()

                if error is not None:
                    form.add_error(field=None, error=error)

                    return self.form_invalid(form)

            if not self.validate_locked_form(form):
                return self.form_invalid(form)

            return super().form_valid(form)

    def get_quota_error(self) -> str | None:
        """Return an error message when the subscription quota is reached."""

        if self.is_quota_exceeded():
            return "You have reached the limit of your plan."

        return None
