from django.test import TestCase

from django.contrib.auth import get_user_model

from django_omise.models.core import Customer
from django_omise.models.schedule import ChargeSchedule
from django_omise.models.choices import Currency, SchedulePeriod


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

    def test_charge_schedule_human_amount(self):
        charge_schedule = ChargeSchedule.objects.create(
            id="test_charge_schedule_id",
            amount=100000,
            currency=Currency.THB,
            livemode=False,
            card=self.customer.cards.live().first(),
            customer=self.customer,
            default_card=False,
        )

        self.assertEqual(charge_schedule.human_amount, "1,000.00")

    def test_charge_schedule_human_amount_jpy(self):
        charge_schedule = ChargeSchedule.objects.create(
            id="test_charge_schedule_id",
            amount=100000,
            currency=Currency.JPY,
            livemode=False,
            card=self.customer.cards.live().first(),
            customer=self.customer,
            default_card=False,
        )

        self.assertEqual(charge_schedule.human_amount, "100,000.00")
