from rest_framework import serializers

from vehicles.models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    """Serialize vehicle data for read-only API responses."""

    class Meta:
        model = Vehicle
        fields = (
            "id",
            "brand",
            "model",
            "year",
            "current_mileage",
        )

        read_only_fields = fields
