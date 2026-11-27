from typing import Any

from django.db.models import QuerySet
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseBase
from django.shortcuts import get_object_or_404
from django.urls import reverse

from vehicles.models import Vehicle


class VehicleScopedMixin:
    """Resolve the requested vehicle and make it available throughout the view.

    The vehicle must belong to the current user. Use this mixin after
    LoginRequiredMixin in views that manage vehicle-related records.
    """

    vehicle: Vehicle

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        """Retrieve the vehicle from the URL and verify ownership.

        Raise Http404 if the vehicle does not exist or belongs to another user.
        """

        self.vehicle = get_object_or_404(
            Vehicle,
            pk=kwargs["pk"],
            owner_id=request.user.pk,
        )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Include the resolved vehicle in the template context."""

        context = super().get_context_data(**kwargs)
        context["vehicle"] = self.vehicle
        return context


class VehicleCreateMixin(VehicleScopedMixin):
    """Handle the creation of records associated with a specific vehicle.

    Assign the vehicle automatically and redirect to its detail page
    after successful creation.
    """

    def form_valid(self, form: ModelForm) -> HttpResponse:
        """Associate the new record with the resolved vehicle before saving."""

        form.instance.vehicle = self.vehicle
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Return the detail page URL of the vehicle associated with the new record."""

        return reverse("vehicles:vehicle-detail", kwargs={"pk": self.vehicle.pk})


class VehicleListMixin(VehicleScopedMixin):
    """Provide a filtered list of records belonging to a specific vehicle.

    Reuse the vehicle resolved by VehicleScopedMixin to restrict
    the queryset without repeating the ownership check.
    """

    def get_queryset(self) -> QuerySet:
        """Return records associated with the previously resolved vehicle."""

        return super().get_queryset().filter(vehicle=self.vehicle)


class OwnedVehicleRecordMixin:
    """Restrict access to records through their related vehicle.

    Used by detail, update and delete views where the URL identifies
    a record rather than the vehicle itself.
    """

    request: HttpRequest

    def get_queryset(self) -> QuerySet:
        """Return records associated with vehicles owned by the current user.

        Fetch the related vehicle in the same query to avoid an additional
        database lookup when accessing it.
        """

        return (
            super()
            .get_queryset()
            .filter(
                vehicle__owner_id=self.request.user.pk,
            )
            .select_related("vehicle")
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Include the vehicle associated with the current record in the context."""

        context = super().get_context_data(**kwargs)
        context["vehicle"] = self.object.vehicle
        return context


class OwnedObjectMixin:
    """Restrict access to objects directly owned by the current user.

    Applicable to any model with an owner relationship, including
    vehicles and custom maintenance items.
    """

    request: HttpRequest

    def get_queryset(self) -> QuerySet:
        """Filter the base queryset to include only objects owned by the current user."""

        return super().get_queryset().filter(owner_id=self.request.user.pk)
