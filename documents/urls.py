from django.urls import include, path

from documents.views import (
    VehicleDocumentCreateView,
    VehicleDocumentDeleteView,
    VehicleDocumentDetailView,
    VehicleDocumentListView,
    VehicleDocumentUpdateView,
)

app_name = "documents"

vehicle_document_detail_patterns = [
    path(
        "",
        VehicleDocumentDetailView.as_view(),
        name="vehicle-document-detail",
    ),
    path(
        "edit/",
        VehicleDocumentUpdateView.as_view(),
        name="vehicle-document-update",
    ),
    path(
        "delete/",
        VehicleDocumentDeleteView.as_view(),
        name="vehicle-document-delete",
    ),
]

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
        include(vehicle_document_detail_patterns),
    ),
]
