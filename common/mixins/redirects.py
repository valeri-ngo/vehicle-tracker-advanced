from django.urls import reverse


class RedirectToDetailMixin:
    """Redirect to the detail page of the current object after a successful operation.

    Require the implementing view to define the detail URL name.
    """

    detail_url_name: str

    def get_success_url(self) -> str:
        """Build the detail URL using the primary key of the current object."""

        return reverse(
            self.detail_url_name,
            kwargs={"pk": self.object.pk},
        )


class RedirectToVehicleListMixin:
    """Redirect to the list of records associated with the current object's vehicle.

    Require the implementing view to define the vehicle-specific list URL name.
    """

    vehicle_list_url_name: str

    def get_success_url(self) -> str:
        """Build the record list URL using the associated vehicle's primary key."""

        return reverse(
            self.vehicle_list_url_name,
            kwargs={"pk": self.object.vehicle_id},
        )
