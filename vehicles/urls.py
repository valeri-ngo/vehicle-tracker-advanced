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

detailed_paths = [
    path("", view=VehicleDetailView.as_view(), name="vehicle-detail"),
    path("edit/", view=VehicleUpdateView.as_view(), name="vehicle-update"),
    path("delete/", view=VehicleDeleteView.as_view(), name="vehicle-delete"),
    path(
        "odometer/add/", view=OdometerEntryCreateView.as_view(), name="odometer-create"
    ),
]

urlpatterns = [
    path("", view=VehicleListView.as_view(), name="vehicle-list"),
    path("add/", view=VehicleCreateView.as_view(), name="vehicle-create"),
    path("<int:pk>/", include(detailed_paths)),
]
