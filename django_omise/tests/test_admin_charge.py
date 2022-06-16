from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

from django_omise.admin import ChargeAdmin
from django_omise.models.core import Charge
from django_omise.models.choices import Currency, ChargeStatus

from django_omise.tests.base import ClientAndUserBaseTestCase
from django_omise.tests.mock_django import MockRequest

from unittest import mock


User = get_user_model()


class AdminTestCase(ClientAndUserBaseTestCase):
    def test_charge_chage_permission(self):
        charge_admin = ChargeAdmin(model=Charge, admin_site=AdminSite())
        request = MockRequest(user=self.user)
        self.assertEqual(charge_admin.has_change_permission(request=request), False)

    @mock.patch("django_omise.admin.admin.format_html")
    def test_charge_colorized_status_successful(self, mock_format_html):
        charge_admin = ChargeAdmin(model=Charge, admin_site=AdminSite())

        charge = self.create_charge(status=ChargeStatus.SUCCESSFUL)
        charge_admin.colorized_status(obj=charge)
        mock_format_html.assert_called_once()

    @mock.patch("django_omise.admin.admin.format_html")
    def test_charge_colorized_status_pending(self, mock_format_html):
        charge_admin = ChargeAdmin(model=Charge, admin_site=AdminSite())

        charge = self.create_charge(status=ChargeStatus.PENDING)
        charge_admin.colorized_status(obj=charge)
        mock_format_html.assert_called_once()

    @mock.patch("django_omise.admin.admin.format_html")
    def test_charge_colorized_status_failed(self, mock_format_html):
        charge_admin = ChargeAdmin(model=Charge, admin_site=AdminSite())

        charge = self.create_charge(status=ChargeStatus.FAILED)
        charge_admin.colorized_status(obj=charge)
        mock_format_html.assert_called_once()

    @mock.patch("django_omise.admin.admin.format_html")
    def test_charge_colorized_status_partially_refunded(self, mock_format_html):
        charge_admin = ChargeAdmin(model=Charge, admin_site=AdminSite())

        charge = self.create_charge(
            status=ChargeStatus.SUCCESSFUL,
            refunded_amount=10000,
        )
        charge_admin.colorized_status(obj=charge)
        mock_format_html.assert_called_once()

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
