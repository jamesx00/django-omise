from django.test import TestCase

from django.contrib.auth import get_user_model

from django_omise.models.core import Customer, Card

from unittest import mock

from .test_utils import mocked_requests_post, mocked_requests_get

User = get_user_model()

# Create your tests here.
class CustomerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test_user1")

        post_patcher = mock.patch("requests.post", side_effect=mocked_requests_post)
        get_patcher = mock.patch("requests.get", side_effect=mocked_requests_get)
        post_patcher.start()
        get_patcher.start()

    def tearDown(self):
        mock.patch.stopall()

    def test_create_customer(self):
        customer, created = Customer.get_or_create(user=self.user)
        self.assertTrue(created)

        customer, created = Customer.get_or_create(user=self.user)
        self.assertFalse(created)

        self.assertEqual(customer.user, self.user)
        self.assertEqual(customer.id, customer.get_omise_object().id)
