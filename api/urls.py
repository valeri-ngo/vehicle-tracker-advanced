from django.urls import path

from api.views import VehicleDetailAPIView, VehicleListAPIView

app_name = "api"

urlpatterns = [
    path("vehicles/", VehicleListAPIView.as_view(), name="vehicle-list"),
    path("vehicles/<int:pk>/", VehicleDetailAPIView.as_view(), name="vehicle-detail"),
]
