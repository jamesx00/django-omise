from django.test import TestCase

from django.contrib.auth import get_user_model

from django_omise.models.core import Customer
from django_omise.models.schedule import Schedule, ChargeSchedule
from django_omise.models.choices import Currency, SchedulePeriod, ScheduleStatus


from django.utils import timezone

from unittest import mock

from .test_utils import (
    mocked_requests_post,
    mocked_requests_get,
    mocked_add_card_request,
    mocked_delete_card_request,
)

User = get_user_model()

# Create your tests here.
class CustomerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user1", email="test_user1@email.com"
        )

        self.post_patcher = mock.patch(
            "requests.post", side_effect=mocked_requests_post
        )
        self.get_patcher = mock.patch("requests.get", side_effect=mocked_requests_get)

        self.post_patcher.start()
        self.get_patcher.start()

        self.customer, self.created = Customer.get_or_create(user=self.user)
        self.customer.sync_cards()

    def tearDown(self):
        mock.patch.stopall()

    def test_create_customer(self):
        self.assertTrue(self.created)

        self.customer, created = Customer.get_or_create(user=self.user)
        self.assertFalse(created)

        self.assertEqual(self.customer.user, self.user)
        self.assertEqual(self.customer.id, self.customer.get_omise_object().id)

    def test_create_customer_wrong_mode(self):
        with self.settings(OMISE_LIVE_MODE=True), self.assertRaises(ValueError):
            customer, created = Customer.get_or_create(user=self.user)

    def test_sync_customer_cards(self):
        omise_customer = self.customer.get_omise_object()

        self.assertEqual(self.customer.cards.count(), len(omise_customer.cards))

    def test_customer_str_with_user(self):
        self.assertIn(str(self.user), str(self.customer))

    def test_customer_str_without_user(self):
        customer = Customer.objects.create(id="customer_test_id", livemode=False)
        self.assertIn("customer_test_id", str(customer))

    @mock.patch("requests.patch", side_effect=mocked_add_card_request)
    def test_add_card_to_customer(self, mocked_request):
        initial_card_count = self.customer.cards.count()
        self.customer.add_card(token="test_token_id")
        self.assertEqual(initial_card_count + 1, self.customer.cards.count())

    @mock.patch("requests.delete", side_effect=mocked_delete_card_request)
    def test_delete_card(self, mock_request):
        live_cards_count = self.customer.cards.live().count()

        self.customer.remove_card(card=self.customer.cards.first())

        self.assertEqual(live_cards_count - 1, self.customer.cards.live().count())

    @mock.patch("django_omise.models.core.Charge.charge")
    def test_charge_with_card(self, mock_charge):
        self.customer.charge_with_card(
            amount=100000,
            currency=Currency.THB,
            card=self.customer.cards.live().first(),
        )

        mock_charge.assert_called_once()

        args, kwargs = mock_charge.call_args
        self.assertEqual(kwargs["card"], self.customer.cards.live().first())

    def test_schedules(self):
        self.customer, created = Customer.get_or_create(user=self.user)
        self.customer.sync_cards()

        charge_schedule = ChargeSchedule.objects.create(
            id="test_charge_schedule_id",
            amount=100000,
            currency=Currency.THB,
            livemode=False,
            card=self.customer.cards.live().first(),
            customer=self.customer,
            default_card=False,
        )

        schedule = Schedule.objects.create(
            id="test_schedule_id",
            livemode=False,
            active=True,
            charge=charge_schedule,
            end_on=timezone.now().date(),
            ended_at=timezone.now(),
            every=1,
            period=SchedulePeriod.DAY,
            start_on=timezone.now().date(),
            status=ScheduleStatus.RUNNING,
        )

        self.assertIn(schedule, self.customer.schedules.all())

    @mock.patch(
        "django_omise.models.schedule.Schedule.update_or_create_from_omise_object"
    )
    @mock.patch("django_omise.models.core.omise.Schedule.create")
    def test_create_schedule_without_card(
        self, mock_schedule_create, mock_update_or_create_method
    ):
        self.customer.create_schedule(
            amount=100000,
            currency=Currency.THB,
            every=1,
            period=SchedulePeriod.DAY,
            start_date=timezone.now(),
            end_date=timezone.now(),
        )

        args, kwargs = mock_schedule_create.call_args
        charge_schedule = kwargs["charge"]
        self.assertNotIn("card", charge_schedule)

    @mock.patch(
        "django_omise.models.schedule.Schedule.update_or_create_from_omise_object"
    )
    @mock.patch("django_omise.models.core.omise.Schedule.create")
    def test_create_schedule_with_card(
        self, mock_schedule_create, mock_update_or_create_method
    ):
        self.customer.create_schedule(
            amount=100000,
            currency=Currency.THB,
            card=self.customer.cards.live().first(),
            every=1,
            period=SchedulePeriod.DAY,
            start_date=timezone.now(),
            end_date=timezone.now(),
        )

        args, kwargs = mock_schedule_create.call_args
        charge_schedule = kwargs["charge"]
        self.assertIn("card", charge_schedule)

    @mock.patch(
        "django_omise.models.schedule.Schedule.update_or_create_from_omise_object"
    )
    @mock.patch("django_omise.models.core.omise.Schedule.create")
    def test_create_schedule_without_description(
        self, mock_schedule_create, mock_update_or_create_method
    ):
        self.customer.create_schedule(
            amount=100000,
            currency=Currency.THB,
            card=self.customer.cards.live().first(),
            every=1,
            period=SchedulePeriod.DAY,
            start_date=timezone.now(),
            end_date=timezone.now(),
        )

        args, kwargs = mock_schedule_create.call_args
        charge_schedule = kwargs["charge"]
        self.assertNotIn("description", charge_schedule)

    @mock.patch(
        "django_omise.models.schedule.Schedule.update_or_create_from_omise_object"
    )
    @mock.patch("django_omise.models.core.omise.Schedule.create")
    def test_create_schedule_with_description(
        self, mock_schedule_create, mock_update_or_create_method
    ):
        description = "Test description"
        self.customer.create_schedule(
            amount=100000,
            currency=Currency.THB,
            card=self.customer.cards.live().first(),
            description=description,
            every=1,
            period=SchedulePeriod.DAY,
            start_date=timezone.now(),
            end_date=timezone.now(),
        )

        args, kwargs = mock_schedule_create.call_args
        charge_schedule = kwargs["charge"]
        self.assertIn("description", charge_schedule)
