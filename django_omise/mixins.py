from .forms import CheckoutWithCardsForm
from .models.core import Customer, Charge, Card
from .models.choices import Currency, ChargeStatus
from .omise import omise

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.views.generic import FormView

from typing import Dict


class CheckoutWithCardsMixin(FormView):
    form_class = CheckoutWithCardsForm

    def charge_with_card(self, card: Card) -> Charge:
        """
        Charge the user with selected card.

        :returns: An instance of Charge object
        """
        customer = self.get_omise_customer()
        charge_details = self.get_charge_details()
        charge = customer.charge_with_card(
            amount=charge_details["amount"],
            currency=charge_details["currency"],
            card=card,
            **self.get_charge_kwargs(),
        )

        return charge

    def get_charge_details(self) -> Dict[int, Currency]:
        """
        Overwrite this method to provide the charge amount and currency.

        Read more on the amount and currency here https://www.omise.co/currency-and-amount

        :returns: Dictionary of charge amount in the smallest unit (int) and the 3-digit currency code. {"amount": int, "currency": str}
        """

    def get_omise_customer(self) -> Customer:
        """
        Overwrite this method to provide the customer instance to charge.

        :returns: An instance of Customer
        """
        if self.request.user.is_authenticated:
            customer, created = Customer.get_or_create(user=self.request.user)
            return customer

    def get_charge_kwargs(self) -> Dict:
        """
        Overwrite this method to add charge parameters.

        :return: A dictionary of charge parameters
        """
        return dict()

    def form_valid(self, form):

        selected_card = form.cleaned_data["card"]

        try:
            charge = self.charge_with_card(card=selected_card)
        except omise.errors.InvalidChargeError as e:
            messages.error(
                self.request,
                f"Payment failed: {str(e)}",
            )
            return super().form_invalid(form)

        self.process_new_charge(charge)

        if charge.status == ChargeStatus.FAILED:
            messages.error(
                self.request,
                f"Payment failed: {charge.failure_message}",
            )
            return super().form_invalid(form)

        if charge.status == ChargeStatus.PENDING:
            return redirect(charge.authorize_uri)

        if charge.status == ChargeStatus.SUCCESSFUL:
            messages.success(self.request, _("Payment successful."))

        return super().form_valid(form)

    def process_new_charge(self, charge: Charge):
        """
        Overwrite this method to process the new charge object.

        :params charge: The new Charge object.
        """
        pass
