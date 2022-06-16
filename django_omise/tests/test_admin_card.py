from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

from django_omise.admin import CardInline
from django_omise.models.core import Customer

from django_omise.tests.base import ClientAndUserBaseTestCase, OmiseBaseTestCase
from django_omise.tests.mock_django import MockRequest

User = get_user_model()


class AdminCardTestCase(ClientAndUserBaseTestCase, OmiseBaseTestCase):
    def test_card_inline_has_change_permission(self):
        card_inline = CardInline(parent_model=Customer, admin_site=AdminSite())
        request = MockRequest(user=self.user)
        self.assertFalse(card_inline.has_change_permission(request=request))

    def test_card_inline_is_not_default_card(self):

        card_inline = CardInline(parent_model=Customer, admin_site=AdminSite())
        card = self.create_card()
        self.assertFalse(card_inline.default_card(obj=card))

    def test_card_inline_is_default_card(self):

        card_inline = CardInline(parent_model=Customer, admin_site=AdminSite())
        card = self.create_card()
        customer = self.create_customer()

        card.customer = customer
        card.save()

        customer.default_card = card
        customer.save()

        self.assertTrue(card_inline.default_card(obj=card))
