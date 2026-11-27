from django.db.models import QuerySet
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from api.serializers import VehicleSerializer
from vehicles.models import Vehicle

from .permissions import HasVIPSubscription


class BaseVehicleAPIView(GenericAPIView):
    """Provide shared configuration and ownership filtering for vehicle API views."""

    serializer_class = VehicleSerializer
    permission_classes = (
        IsAuthenticated,
        HasVIPSubscription,
    )

    def get_queryset(self) -> QuerySet[Vehicle]:
        """Return vehicles belonging to the current user."""

        return Vehicle.objects.filter(owner=self.request.user)


class VehicleListAPIView(ListAPIView, BaseVehicleAPIView):
    """Provide a read-only list of vehicles owned by the authenticated user."""


class VehicleDetailAPIView(RetrieveAPIView, BaseVehicleAPIView):
    """Provide read-only details of a vehicle owned by the authenticated user."""
