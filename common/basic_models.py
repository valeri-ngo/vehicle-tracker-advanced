from django.db import models


class CreatedAtModel(models.Model):
    """Provide a creation timestamp for inheriting Django models."""

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ("-created_at",)


class DateTimeModel(CreatedAtModel):
    """Provide creation and last-update timestamps for inheriting models."""

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta(CreatedAtModel.Meta):
        abstract = True
