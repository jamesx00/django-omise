from django.test import TestCase

from django.contrib.auth import get_user_model

from django_omise.models.core import Customer, Card, Charge
from django_omise.models.choices import Currency
from django_omise.omise import omise

from django_omise.utils.core_utils import update_or_create_from_omise_object

from unittest import mock

from .test_utils import (
    mocked_fully_refunded_charge_request,
    mocked_requests_post,
    mocked_requests_get,
    mocked_charge_with_card_request,
    mocked_partially_refunded_charge_request,
    mocked_fully_refunded_charge_request,
    mocked_base_charge_request,
    mocked_jpy_charge,
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

        self.customer, created = Customer.get_or_create(user=self.user)
        self.customer.sync_cards()

    def tearDown(self):
        mock.patch.stopall()

    def test_no_charge_type_error(self):
        with self.assertRaises(
            ValueError, msg="At least a token, a card, or a source is required"
        ):
            Charge.charge(amount=100000, currency=Currency.THB)

    def test_more_than_one_charge_type_error(self):
        with self.assertRaises(
            ValueError, msg="Only one of token, card, or source must be specified"
        ):
            Charge.charge(amount=100000, currency=Currency.THB, token="123", card="123")

    @mock.patch("requests.post", side_effect=mocked_charge_with_card_request)
    @mock.patch("requests.get", side_effect=mocked_charge_with_card_request)
    def test_charge(self, mocked_post_request, mocked_get_request):
        charge = Charge.charge(
            amount=100000,
            currency=Currency.THB,
            card=self.customer.cards.live().first(),
        )
        self.assertEqual(charge.amount, charge.get_omise_object().amount)
        self.assertEqual(charge.id, charge.get_omise_object().id)

    @mock.patch("requests.post", side_effect=mocked_charge_with_card_request)
    @mock.patch("requests.get", side_effect=mocked_charge_with_card_request)
    def test_charge_human_amount(self, mocked_post_request, mocked_get_request):
        unsaved_charge = Charge(amount=100000)
        self.assertEqual(unsaved_charge.human_amount, 0)

        charge = Charge.charge(
            amount=100000,
            currency=Currency.THB,
            card=self.customer.cards.live().first(),
        )

        self.assertEqual(charge.human_amount, "1,000.00")

    @mock.patch("requests.post", side_effect=mocked_jpy_charge)
    @mock.patch("requests.get", side_effect=mocked_jpy_charge)
    def test_charge_human_amount_jpy(self, mocked_post_request, mocked_get_request):
        charge = Charge.charge(
            amount=100000,
            currency=Currency.JPY,
            card=self.customer.cards.live().first(),
        )

        self.assertEqual(charge.human_amount, "100,000.00")

    @mock.patch("requests.get", side_effect=mocked_partially_refunded_charge_request)
    def test_charge_extended_status_partially_refund(self, mocked_api):
        omise_charge = omise.Charge.retrieve("charge_id")
        charge = update_or_create_from_omise_object(omise_object=omise_charge)

        self.assertEqual(charge.extended_status, "partially refunded")

    @mock.patch("requests.get", side_effect=mocked_fully_refunded_charge_request)
    def test_charge_extended_status_fully_refund(self, mocked_api):
        omise_charge = omise.Charge.retrieve("charge_id")
        charge = update_or_create_from_omise_object(omise_object=omise_charge)

        self.assertEqual(charge.extended_status, "refunded")

    @mock.patch("requests.get", side_effect=mocked_base_charge_request)
    def test_charge_extended_status_normal(self, mocked_api):
        omise_charge = omise.Charge.retrieve("charge_id")
        charge = update_or_create_from_omise_object(omise_object=omise_charge)

        self.assertEqual(charge.extended_status, omise_charge.status)

    @mock.patch("django_omise.models.core.Charge.update_or_create_from_omise_object")
    @mock.patch("django_omise.models.core.omise.Charge.create")
    @mock.patch("requests.post", side_effect=mocked_base_charge_request)
    def test_create_charge_with_card_passed_arguments(
        self,
        mock_request,
        mock_omise,
        mock_update_or_create_method,
    ):

        charge = Charge.charge(
            amount=100000,
            currency=Currency.THB,
            card=self.customer.cards.live().first(),
        )

        args, kwargs = mock_omise.call_args
        self.assertIn("customer", kwargs)
        self.assertIn("card", kwargs)

    @mock.patch("django_omise.models.core.Charge.update_or_create_from_omise_object")
    @mock.patch("django_omise.models.core.omise.Charge.create")
    @mock.patch("requests.post", side_effect=mocked_base_charge_request)
    def test_create_charge_with_token_as_string_passed_arguments(
        self,
        mock_request,
        mock_omise,
        mock_update_or_create_method,
    ):

        charge = Charge.charge(amount=100000, currency=Currency.THB, token="token_id")

        args, kwargs = mock_omise.call_args
        self.assertEqual(kwargs["card"], "token_id")

    @mock.patch("django_omise.models.core.Charge.update_or_create_from_omise_object")
    @mock.patch("django_omise.models.core.omise.Charge.create")
    @mock.patch("requests.post", side_effect=mocked_base_charge_request)
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_create_charge_with_token_as_token_instance_passed_arguments(
        self,
        mock_get_requests,
        mock_request,
        mock_omise,
        mock_update_or_create_method,
    ):

        token = omise.Token.retrieve("test_token_id")

        charge = Charge.charge(amount=100000, currency=Currency.THB, token=token)

        args, kwargs = mock_omise.call_args
        self.assertIn("card", kwargs)

    @mock.patch("django_omise.models.core.Charge.update_or_create_from_omise_object")
    @mock.patch("django_omise.models.core.omise.Charge.create")
    @mock.patch("requests.post", side_effect=mocked_base_charge_request)
    def test_create_charge_with_source_passed_arguments(
        self,
        mock_request,
        mock_omise,
        mock_update_or_create_method,
    ):

        charge = Charge.charge(
            amount=100000, currency=Currency.THB, source={"type": "promptpay"}
        )

        args, kwargs = mock_omise.call_args
        self.assertIn("source", kwargs)
