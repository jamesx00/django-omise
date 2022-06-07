from django.test import TestCase

from django_omise.models.core import Refund
from django_omise.models.choices import Currency

# Create your tests here.
class RefundTestCase(TestCase):
    def test_refund_human_amount(self):
        refund = Refund(amount=100000, currency=Currency.THB)
        self.assertEqual(refund.human_amount, "1,000.00")

    def test_refund_human_amount_jpy(self):
        refund = Refund(amount=100000, currency=Currency.JPY)
        self.assertEqual(refund.human_amount, "100,000.00")
