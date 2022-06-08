from django.test import TestCase

from django.contrib.auth import get_user_model

from django_omise.models.core import Customer, Card
from django_omise.omise import omise
from django_omise.utils.core_utils import get_model_from_omise_object

from unittest import mock


from .test_utils import (
    mocked_requests_post,
    mocked_requests_get,
)

User = get_user_model()

# Create your tests here.
class CoreUtilTestCase(TestCase):
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

    def test_get_model_from_omise_object_customer(self):
        customer = omise.Customer.retrieve("test_customer_id")
        self.assertEqual(get_model_from_omise_object(omise_object=customer), Customer)

    def test_get_model_from_omise_object_card(self):
        customer = omise.Customer.retrieve("test_customer_id")
        card = customer.cards[0]
        self.assertEqual(get_model_from_omise_object(omise_object=card), Card)
