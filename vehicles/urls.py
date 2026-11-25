from django.urls import include, path

from .views import (
    OdometerEntryCreateView,
    VehicleCreateView,
    VehicleDeleteView,
    VehicleDetailView,
    VehicleListView,
    VehicleUpdateView,
)

app_name = "vehicles"

vehicle_detail_patterns = [
    path("", VehicleDetailView.as_view(), name="vehicle-detail"),
    path("edit/", VehicleUpdateView.as_view(), name="vehicle-update"),
    path("delete/", VehicleDeleteView.as_view(), name="vehicle-delete"),
    path(
        "odometer/add/", OdometerEntryCreateView.as_view(), name="odometer-create"
    ),
]

urlpatterns = [
    path("", VehicleListView.as_view(), name="vehicle-list"),
    path("add/", VehicleCreateView.as_view(), name="vehicle-create"),
    path("<int:pk>/", include(vehicle_detail_patterns)),
]
