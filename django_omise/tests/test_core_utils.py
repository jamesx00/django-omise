from django.contrib.auth import get_user_model

from django_omise.models.core import Customer, Card, Charge
from django_omise.models.choices import Currency
from django_omise.omise import omise
from django_omise.utils.core_utils import (
    get_model_from_omise_object,
)

from django_omise.tests.base import OmiseBaseTestCase

from unittest import mock


from .test_utils import (
    mocked_requests_post,
    mocked_requests_get,
    mocked_base_charge_request,
)

User = get_user_model()

# Create your tests here.
class CoreUtilTestCase(OmiseBaseTestCase):
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

    @mock.patch("requests.post", side_effect=mocked_base_charge_request)
    def test_get_model_from_omise_object_charge(self, mock_charge_request):
        charge = omise.Charge.create(
            amount=100000,
            currency=Currency.THB,
            card=self.customer.cards.live().first().id,
        )

        self.assertEqual(get_model_from_omise_object(omise_object=charge), Charge)

    def test_get_model_from_omise_object_not_implemented(self):
        new_object = type("test", (object,), {})()
        new_object.object = "new_object"
        self.assertEqual(get_model_from_omise_object(omise_object=new_object), None)

    def test_get_model_from_omise_object_not_implemented_raises(self):
        new_object = type("test", (object,), {})()
        new_object.object = "new_object"
        with self.assertRaises(ValueError):
            get_model_from_omise_object(
                omise_object=new_object, raise_if_not_implemented=True
            )
