from django.contrib.auth import get_user_model

from django.test import Client, TestCase

from django_omise.models.core import Customer, Card, Charge, Source
from django_omise.models.choices import ChargeStatus, Currency

User = get_user_model()


class ClientAndUserBaseTestCase(TestCase):
    """Base TestCase with utilites to create user and login client."""

    def setUp(self):
        """Class setup."""
        self.client = Client()
        self.index_url = "/"
        self.login()

    def create_user(self):
        """Create user and returns username, password tuple."""
        username, password = "admin", "test"
        user = User.objects.get_or_create(
            username=username,
            email="admin@test.com",
            is_superuser=True,
            is_staff=True,
        )[0]
        user.set_password(password)
        user.save()
        self.user = user
        return (username, password)

    def login(self):
        """Log in client session."""
        username, password = self.create_user()
        self.client.login(username=username, password=password)


class OmiseBaseTestCase(TestCase):
    def create_card(self, **kwargs):
        default = {
            "id": "test_card_id",
            "livemode": False,
        }

        default.update(kwargs)

        return Card.objects.create(**default)

    def create_source(self, **kwargs):
        default = {
            "id": "test_source_id",
            "livemode": True,
            "amount": 100000,
            "currency": Currency.THB,
        }

        default.update(kwargs)
        return Source.objects.create(**default)

    def create_customer(self, **kwargs):
        default = {
            "id": "test_customer_id",
            "livemode": False,
        }
        default.update(kwargs)
        return Customer.objects.create(**default)

    def create_charge(self, **kwargs):
        default = {
            "id": "test_charge_id",
            "livemode": False,
            "status": ChargeStatus.SUCCESSFUL,
            "amount": 1000000,
            "currency": Currency.THB,
            "fee": 0,
            "fee_vat": 0,
            "net": 0,
            "paid": True,
            "refundable": True,
            "refunded_amount": 0,
        }
        default.update(kwargs)
        charge = Charge.objects.create(
            **default,
        )
        return charge
