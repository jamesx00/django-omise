from django.test import Client, TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

from django_omise.admin import ChargeAdmin
from django_omise.models.core import Charge
from django_omise.models.choices import Currency, ChargeStatus

from django_omise.tests.mock_django import MockRequest

from unittest import mock


User = get_user_model()


class BaseTestCase(TestCase):
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


class AdminTestCase(BaseTestCase):
    def test_charge_chage_permission(self):
        charge_admin = ChargeAdmin(model=Charge, admin_site=AdminSite())
        request = MockRequest(user=self.user)
        self.assertEqual(charge_admin.has_change_permission(request=request), False)

    def test_charge_colorized_status_successful(self):
        charge_admin = ChargeAdmin(model=Charge, admin_site=AdminSite())

        charge = self.create_charge(status=ChargeStatus.SUCCESSFUL)
        try:
            charge_admin.colorized_status(obj=charge)
        except Exception as e:
            self.fail(
                f"ChargeAdmin.colorized_status should not raise an error. An error was raised {type(e)}: {e}"
            )

    def test_charge_colorized_status_pending(self):
        charge_admin = ChargeAdmin(model=Charge, admin_site=AdminSite())

        charge = self.create_charge(status=ChargeStatus.PENDING)
        try:
            charge_admin.colorized_status(obj=charge)
        except Exception as e:
            self.fail(
                f"ChargeAdmin.colorized_status should not raise an error. An error was raised {type(e)}: {e}"
            )

    def test_charge_colorized_status_failed(self):
        charge_admin = ChargeAdmin(model=Charge, admin_site=AdminSite())

        charge = self.create_charge(status=ChargeStatus.FAILED)
        try:
            charge_admin.colorized_status(obj=charge)
        except Exception as e:
            self.fail(
                f"ChargeAdmin.colorized_status should not raise an error. An error was raised {type(e)}: {e}"
            )

    def test_charge_colorized_status_failed(self):
        charge_admin = ChargeAdmin(model=Charge, admin_site=AdminSite())

        charge = self.create_charge(status=ChargeStatus.FAILED)
        try:
            charge_admin.colorized_status(obj=charge)
        except Exception as e:
            self.fail(
                f"ChargeAdmin.colorized_status should not raise an error. An error was raised {type(e)}: {e}"
            )

    def test_charge_colorized_status_failed(self):
        charge_admin = ChargeAdmin(model=Charge, admin_site=AdminSite())

        charge = self.create_charge(status=ChargeStatus.FAILED)
        try:
            charge_admin.colorized_status(obj=charge)
        except Exception as e:
            self.fail(
                f"ChargeAdmin.colorized_status should not raise an error. An error was raised {type(e)}: {e}"
            )

    def test_charge_colorized_status_partially_refunded(self):
        charge_admin = ChargeAdmin(model=Charge, admin_site=AdminSite())

        charge = self.create_charge(
            status=ChargeStatus.SUCCESSFUL,
            refunded_amount=10000,
        )
        try:
            charge_admin.colorized_status(obj=charge)
        except Exception as e:
            self.fail(
                f"ChargeAdmin.colorized_status should not raise an error. An error was raised {type(e)}: {e}"
            )

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
