from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from common.mixins import (
    OwnedVehicleRecordMixin,
    RedirectToDetailMixin,
    RedirectToVehicleListMixin,
    SubscriptionQuotaMixin,
    VehicleCreateMixin,
    VehicleListMixin,
)
from documents.forms import VehicleDocumentForm
from documents.models import VehicleDocument


class VehicleDocumentCreateView(
    LoginRequiredMixin,
    SubscriptionQuotaMixin,
    VehicleCreateMixin,
    CreateView,
):
    """Create a vehicle document within subscription quotas."""

    form_class = VehicleDocumentForm
    template_name = "documents/vehicle_document_form.html"
    quota_resource = "documents"

    def get_quota_queryset(self) -> QuerySet:
        """Return all vehicle documents owned by the current user."""

        return VehicleDocument.objects.filter(
            vehicle__owner=self.request.user,
        )


class VehicleDocumentListView(
    LoginRequiredMixin,
    VehicleListMixin,
    ListView,
):
    model = VehicleDocument
    template_name = "documents/vehicle_document_list.html"
    context_object_name = "documents"


class VehicleDocumentDetailView(
    LoginRequiredMixin,
    OwnedVehicleRecordMixin,
    DetailView,
):
    model = VehicleDocument
    template_name = "documents/vehicle_document_detail.html"
    context_object_name = "document"


class VehicleDocumentUpdateView(
    LoginRequiredMixin,
    RedirectToDetailMixin,
    OwnedVehicleRecordMixin,
    UpdateView,
):
    model = VehicleDocument
    form_class = VehicleDocumentForm
    template_name = "documents/vehicle_document_form.html"
    context_object_name = "document"
    detail_url_name = "documents:vehicle-document-detail"


class VehicleDocumentDeleteView(
    LoginRequiredMixin,
    RedirectToVehicleListMixin,
    OwnedVehicleRecordMixin,
    DeleteView,
):
    model = VehicleDocument
    template_name = "documents/vehicle_document_delete.html"
    context_object_name = "document"
    vehicle_list_url_name = "documents:vehicle-document-list"
