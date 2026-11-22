from django.urls import path

from documents.views import (
    VehicleDocumentCreateView,
    VehicleDocumentDeleteView,
    VehicleDocumentDetailView,
    VehicleDocumentListView,
    VehicleDocumentUpdateView,
)

app_name = "documents"

urlpatterns = [
    path(
        "<int:pk>/",
        VehicleDocumentListView.as_view(),
        name="vehicle-document-list",
    ),
    path(
        "<int:pk>/add/",
        VehicleDocumentCreateView.as_view(),
        name="vehicle-document-create",
    ),
    path(
        "records/<int:pk>/",
        VehicleDocumentDetailView.as_view(),
        name="vehicle-document-detail",
    ),
    path(
        "records/<int:pk>/edit/",
        VehicleDocumentUpdateView.as_view(),
        name="vehicle-document-update",
    ),
    path(
        "records/<int:pk>/delete/",
        VehicleDocumentDeleteView.as_view(),
        name="vehicle-document-delete",
    ),
]
