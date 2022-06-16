from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

from django_omise.admin import ChargeAdmin, ChargeInline
from django_omise.models.core import Charge, Source, Card
from django_omise.models.choices import Currency, ChargeStatus

from django_omise.tests.base import ClientAndUserBaseTestCase, OmiseBaseTestCase
from django_omise.tests.mock_django import MockRequest

from unittest import mock


User = get_user_model()


class AdminChargeTestCase(ClientAndUserBaseTestCase, OmiseBaseTestCase):
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

    @mock.patch("django_omise.admin.admin.format_html")
    def test_charge_inline_colorized_status_successful(self, mock_format_html):
        charge_inline = ChargeInline(parent_model=Charge, admin_site=AdminSite())

        charge = self.create_charge(
            status=ChargeStatus.SUCCESSFUL,
        )
        charge_inline.colorized_status(obj=charge)
        mock_format_html.assert_called_once()

    @mock.patch("django_omise.admin.admin.format_html")
    def test_charge_inline_colorized_status_failed(self, mock_format_html):
        charge_inline = ChargeInline(parent_model=Charge, admin_site=AdminSite())

        charge = self.create_charge(
            status=ChargeStatus.FAILED,
        )
        charge_inline.colorized_status(obj=charge)
        mock_format_html.assert_called_once()

    @mock.patch("django_omise.admin.admin.format_html")
    def test_charge_inline_colorized_status_pending(self, mock_format_html):
        charge_inline = ChargeInline(parent_model=Charge, admin_site=AdminSite())

        charge = self.create_charge(
            status=ChargeStatus.PENDING,
        )
        charge_inline.colorized_status(obj=charge)
        mock_format_html.assert_called_once()

    @mock.patch("django_omise.admin.admin.format_html")
    def test_charge_inline_colorized_status_refunded(self, mock_format_html):
        charge_inline = ChargeInline(parent_model=Charge, admin_site=AdminSite())

        charge = self.create_charge(
            status=ChargeStatus.SUCCESSFUL,
            refunded_amount=1000,
        )
        charge_inline.colorized_status(obj=charge)
        mock_format_html.assert_called_once()

    def test_charge_inline_change_permission(self):
        charge_inline = ChargeInline(parent_model=Charge, admin_site=AdminSite())
        request = MockRequest(user=self.user)

        self.assertEqual(charge_inline.has_change_permission(request=request), False)

    def test_charge_source_type_with_card(self):
        charge_admin = ChargeAdmin(model=Charge, admin_site=AdminSite())

        card = self.create_card()
        charge = self.create_charge(status=ChargeStatus.SUCCESSFUL, card=card)
        self.assertIn("card", charge_admin.source_type(obj=charge))

    def test_charge_source_type_with_source(self):
        charge_admin = ChargeAdmin(model=Charge, admin_site=AdminSite())

        source = self.create_source()
        charge = self.create_charge(status=ChargeStatus.SUCCESSFUL, source=source)
        self.assertNotIn("card", charge_admin.source_type(obj=charge))
