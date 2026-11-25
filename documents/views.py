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
    """Register document metadata for a vehicle owned by the user.

    Enforce the document quota defined by the user's subscription plan.
    """

    form_class = VehicleDocumentForm
    template_name = "documents/vehicle_document_form.html"
    quota_resource = "documents"

    def get_quota_queryset(self) -> QuerySet[VehicleDocument]:
        """Return all vehicle documents owned by the current user."""

        return VehicleDocument.objects.filter(
            vehicle__owner=self.request.user,
        )


class VehicleDocumentListView(
    LoginRequiredMixin,
    VehicleListMixin,
    ListView,
):
    """List documents associated with a vehicle owned by the current user."""

    model = VehicleDocument
    template_name = "documents/vehicle_document_list.html"
    context_object_name = "documents"


class VehicleDocumentDetailView(
    LoginRequiredMixin,
    OwnedVehicleRecordMixin,
    DetailView,
):
    """Display document metadata for a vehicle owned by the current user."""

    model = VehicleDocument
    template_name = "documents/vehicle_document_detail.html"
    context_object_name = "document"


class VehicleDocumentUpdateView(
    LoginRequiredMixin,
    RedirectToDetailMixin,
    OwnedVehicleRecordMixin,
    UpdateView,
):
    """Update document metadata owned by the current user.

    Allow changes to expiration dates, reminder preferences and notes.
    """

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
    """Delete vehicle document metadata after user confirmation."""

    model = VehicleDocument
    template_name = "documents/vehicle_document_delete.html"
    context_object_name = "document"
    vehicle_list_url_name = "documents:vehicle-document-list"
