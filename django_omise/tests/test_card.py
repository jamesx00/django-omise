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
class CardTestCase(TestCase):
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

    @mock.patch("requests.delete", side_effect=mocked_delete_card_request)
    def test_delete_card(self, mocked_request):
        customer, created = Customer.get_or_create(user=self.user)
        customer.sync_cards()

        all_cards_count = Card.objects.count()
        Card.objects.first().delete()

        self.assertEqual(Card.objects.count() - 1, Card.objects.live().count())

        self.assertEqual(all_cards_count, Card.objects.count())
