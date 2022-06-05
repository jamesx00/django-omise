from django.test import TestCase

from django.contrib.auth import get_user_model

from django_omise.models.core import Customer, Card

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

    def tearDown(self):
        mock.patch.stopall()

    def test_create_customer(self):
        customer, created = Customer.get_or_create(user=self.user)
        self.assertTrue(created)

        customer, created = Customer.get_or_create(user=self.user)
        self.assertFalse(created)

        self.assertEqual(customer.user, self.user)
        self.assertEqual(customer.id, customer.get_omise_object().id)

    def test_create_customer_wrong_mode(self):
        with self.settings(OMISE_LIVE_MODE=True), self.assertRaises(ValueError):
            customer, created = Customer.get_or_create(user=self.user)

    def test_sync_customer_cards(self):
        customer, created = Customer.get_or_create(user=self.user)
        customer = customer.reload_from_omise()
        customer.sync_cards()

        omise_customer = customer.get_omise_object()

        self.assertEqual(customer.cards.count(), len(omise_customer.cards))

    @mock.patch("requests.patch", side_effect=mocked_add_card_request)
    def test_add_card_to_customer(self, mocked_request):
        customer, created = Customer.get_or_create(user=self.user)
        customer.sync_cards()
        initial_card_count = customer.cards.count()
        customer.add_card(token="test_token_id")
        self.assertEqual(initial_card_count + 1, customer.cards.count())

    @mock.patch("requests.delete", side_effect=mocked_delete_card_request)
    def test_delete_card(self, mock_request):
        customer, created = Customer.get_or_create(user=self.user)
        customer.sync_cards()
        live_cards_count = customer.cards.live().count()

        customer.remove_card(card=customer.cards.first())

        self.assertEqual(live_cards_count - 1, customer.cards.live().count())
