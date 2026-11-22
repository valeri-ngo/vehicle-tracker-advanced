from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import OdometerEntryForm
from .models import OdometerEntry, Vehicle


class OdometerEntryConstraintTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )

        self.vehicle = Vehicle.objects.create(
            owner=self.user,
            brand="BMW",
            model="320d",
            year=2018,
            current_mileage=150000,
        )

        self.recorded_at = timezone.now()

    def test_duplicate_recorded_at_is_rejected(self):
        OdometerEntry.objects.create(
            vehicle=self.vehicle,
            mileage=150000,
            recorded_at=self.recorded_at,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            OdometerEntry.objects.create(
                vehicle=self.vehicle,
                mileage=151000,
                recorded_at=self.recorded_at,
            )

        self.assertEqual(
            OdometerEntry.objects.filter(vehicle=self.vehicle).count(),
            1,
        )

    def test_same_recorded_at_for_different_vehicles_is_allowed(self):
        second_vehicle = Vehicle.objects.create(
            owner=self.user,
            brand="Audi",
            model="A4",
            year=2015,
            current_mileage=220000,
        )

        OdometerEntry.objects.create(
            vehicle=self.vehicle,
            recorded_at=self.recorded_at,
            mileage=150000,
        )

        OdometerEntry.objects.create(
            vehicle=second_vehicle,
            recorded_at=self.recorded_at,
            mileage=220000,
        )

        self.assertEqual(OdometerEntry.objects.count(), 2)


class OdometerEntryFormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123",
        )

        self.vehicle = Vehicle.objects.create(
            owner=self.user,
            brand="Mercedes",
            model="C320d",
            year=2022,
            current_mileage=152000,
        )

        self.recorded_at = timezone.now()

    def test_valid_historical_odometer_entry(self):
        OdometerEntry.objects.create(
            vehicle=self.vehicle,
            mileage=150000,
            recorded_at=self.recorded_at - timedelta(days=2),
        )

        OdometerEntry.objects.create(
            vehicle=self.vehicle,
            mileage=152000,
            recorded_at=self.recorded_at,
        )

        form = OdometerEntryForm(
            data={
                "mileage": 151000,
                "recorded_at": (self.recorded_at - timedelta(days=1)).isoformat(),
            },
            vehicle=self.vehicle,
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_mileage_lower_than_previous_is_rejected(self):
        OdometerEntry.objects.create(
            vehicle=self.vehicle,
            mileage=150000,
            recorded_at=self.recorded_at - timedelta(days=2),
        )

        OdometerEntry.objects.create(
            vehicle=self.vehicle,
            mileage=152000,
            recorded_at=self.recorded_at,
        )

        form = OdometerEntryForm(
            data={
                "mileage": 149000,
                "recorded_at": (self.recorded_at - timedelta(days=1)).isoformat(),
            },
            vehicle=self.vehicle,
        )

        self.assertFalse(form.is_valid(), form.errors)
        self.assertIn("mileage", form.errors)
        self.assertIn(
            "Mileage cannot be lower than the previous one.",
            form.errors["mileage"],
        )

    def test_mileage_higher_than_next_is_rejected(self):
        OdometerEntry.objects.create(
            vehicle=self.vehicle,
            mileage=150000,
            recorded_at=self.recorded_at - timedelta(days=2),
        )

        OdometerEntry.objects.create(
            vehicle=self.vehicle,
            mileage=152000,
            recorded_at=self.recorded_at,
        )

        form = OdometerEntryForm(
            data={
                "mileage": 153000,
                "recorded_at": (self.recorded_at - timedelta(days=1)).isoformat(),
            },
            vehicle=self.vehicle,
        )

        self.assertFalse(form.is_valid(), form.errors)
        self.assertIn("mileage", form.errors)
        self.assertIn(
            "Mileage cannot be higher than the next one.",
            form.errors["mileage"],
        )

    def test_duplicate_recorded_at_is_rejected_by_form(self):
        OdometerEntry.objects.create(
            vehicle=self.vehicle,
            mileage=150000,
            recorded_at=self.recorded_at,
        )

        form = OdometerEntryForm(
            data={
                "mileage": 151000,
                "recorded_at": self.recorded_at.isoformat(),
            },
            vehicle=self.vehicle,
        )

        self.assertFalse(form.is_valid(), form.errors)
        self.assertIn("recorded_at", form.errors)
        self.assertIn(
            "An odometer entry already exists for this date and time.",
            form.errors["recorded_at"],
        )


class OdometerEntryAccessTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="test_pass_123",
        )

        self.vehicle = Vehicle.objects.create(
            owner=self.user,
            brand="BMW",
            model="320d",
            year=2018,
            current_mileage=150000,
        )

    def test_anonymous_access(self):
        url = reverse(
            "vehicles:odometer-create",
            kwargs={"pk": self.vehicle.pk},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_owner_can_access_odometer_form(self):
        self.client.force_login(self.user)

        url = reverse(
            "vehicles:odometer-create",
            kwargs={
                "pk": self.vehicle.pk,
            },
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_access_odometer_form(self):
        second_user = get_user_model().objects.create_user(
            username="second_user",
            password="test_password_123",
        )

        self.client.force_login(second_user)

        url = reverse(
            "vehicles:odometer-create",
            kwargs={
                "pk": self.vehicle.pk,
            },
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_other_user_cannot_create_odometer_entry(self):
        second_user = get_user_model().objects.create_user(
            username="second_user",
            password="test_password_123",
        )

        self.client.force_login(second_user)

        url = reverse(
            "vehicles:odometer-create",
            kwargs={
                "pk": self.vehicle.pk,
            },
        )

        response = self.client.post(
            url,
            data={
                "mileage": 155000,
                "recorded_at": timezone.now().isoformat(),
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(OdometerEntry.objects.filter(vehicle=self.vehicle).count(), 0)

    def test_owner_can_create_odometer_entry(self):
        self.client.force_login(self.user)

        url = reverse(
            "vehicles:odometer-create",
            kwargs={
                "pk": self.vehicle.pk,
            },
        )

        response = self.client.post(
            url,
            data={
                "mileage": 155000,
                "recorded_at": timezone.now().isoformat(),
            },
        )

        entry = OdometerEntry.objects.get(vehicle=self.vehicle)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(OdometerEntry.objects.filter(vehicle=self.vehicle).count(), 1)
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.current_mileage, 155000)
        self.assertEqual(entry.mileage, 155000)

    def test_historical_entry_does_not_reduce_current_mileage(self):
        self.client.force_login(self.user)

        url = reverse(
            "vehicles:odometer-create",
            kwargs={
                "pk": self.vehicle.pk,
            },
        )

        self.vehicle.current_mileage = 155000
        self.vehicle.save(
            update_fields=["current_mileage"],
        )

        now = timezone.now()

        OdometerEntry.objects.create(
            vehicle=self.vehicle,
            mileage=155000,
            recorded_at=now,
        )

        historical_date = now - timedelta(days=1)

        response = self.client.post(
            url,
            data={
                "mileage": 152000,
                "recorded_at": historical_date.isoformat(),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(OdometerEntry.objects.filter(vehicle=self.vehicle).count(), 2)
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.current_mileage, 155000)
        self.assertTrue(
            OdometerEntry.objects.filter(
                vehicle=self.vehicle,
                mileage=152000,
            ).exists()
        )

    def test_odometer_entry_rollback_when_vehicle_save_fails(self):
        self.client.force_login(self.user)

        url = reverse(
            "vehicles:odometer-create",
            kwargs={
                "pk": self.vehicle.pk,
            },
        )

        with (
            patch.object(
                Vehicle,
                "save",
                side_effect=RuntimeError("Simulated database failure."),
            ),
            self.assertRaises(RuntimeError),
        ):
            self.client.post(
                url,
                data={
                    "mileage": 160_000,
                    "recorded_at": timezone.now().isoformat(),
                },
            )

        self.assertFalse(OdometerEntry.objects.filter(vehicle=self.vehicle).exists())
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.current_mileage, 150000)

    def test_select_related_avoids_extra_queries(self):
        now = timezone.now()

        OdometerEntry.objects.create(
            vehicle=self.vehicle,
            mileage=155_000,
            recorded_at=now,
        )

        OdometerEntry.objects.create(
            vehicle=self.vehicle,
            mileage=150_000,
            recorded_at=now - timedelta(days=1),
        )

        OdometerEntry.objects.create(
            vehicle=self.vehicle,
            mileage=130_000,
            recorded_at=now - timedelta(days=2),
        )

        with self.assertNumQueries(1):
            entries = OdometerEntry.objects.select_related("vehicle")

            brands = [entry.vehicle.brand for entry in entries]

        self.assertEqual(len(brands), 3)

    def test_without_select_related_causes_extra_queries(self):
        now = timezone.now()

        OdometerEntry.objects.create(
            vehicle=self.vehicle,
            mileage=130_000,
            recorded_at=now,
        )

        OdometerEntry.objects.create(
            vehicle=self.vehicle,
            mileage=120_000,
            recorded_at=now - timedelta(days=2),
        )

        OdometerEntry.objects.create(
            vehicle=self.vehicle,
            mileage=100_000,
            recorded_at=now - timedelta(days=3),
        )

        with self.assertNumQueries(4):
            entries = OdometerEntry.objects.all()

            brands = [entry.vehicle.brand for entry in entries]

        self.assertEqual(len(brands), 3)

    def test_prefetch_related_avoids_extra_queries(self):
        now = timezone.now()

        vehicle = self.vehicle

        second_vehicle = Vehicle.objects.create(
            owner=self.user,
            brand="BMW",
            model="320d",
            year=2019,
            current_mileage=130_000,
        )

        OdometerEntry.objects.create(
            vehicle=vehicle,
            mileage=150_000,
            recorded_at=now,
        )

        OdometerEntry.objects.create(
            vehicle=vehicle,
            mileage=140_000,
            recorded_at=now - timedelta(days=5),
        )

        OdometerEntry.objects.create(
            vehicle=second_vehicle,
            mileage=130_000,
            recorded_at=now,
        )

        OdometerEntry.objects.create(
            vehicle=second_vehicle,
            mileage=120_000,
            recorded_at=now - timedelta(days=10),
        )

        with self.assertNumQueries(2):
            vehicles = Vehicle.objects.prefetch_related("odometer_entries")

            total_entries = sum(
                len(vehicle.odometer_entries.all()) for vehicle in vehicles
            )

        self.assertEqual(total_entries, 4)
