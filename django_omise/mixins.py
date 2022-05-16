from .forms import CheckoutWithCardsForm, CheckoutForm
from .models.core import Customer, Charge, Card
from .models.choices import Currency, ChargeStatus
from .omise import omise

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.views.generic import FormView

from typing import Dict, Optional


class CheckoutMixin(FormView):
    form_class = CheckoutForm
    template_name = "django_omise/checkout.html"

    def charge(self, payment_method) -> Charge:
        """
        Created a charge with selected payment method.

        :returns: A new Charge instance.
        """
        payment_method_type = type(payment_method)
        charge_details = self.get_charge_details()

        amount = charge_details["amount"]
        currency = charge_details["currency"]

        charge_kwargs = self.get_charge_kwargs()

        if payment_method_type == omise.Token:
            charge = Charge.charge(
                amount=amount,
                currency=currency,
                token=payment_method,
                **charge_kwargs,
            )

        elif payment_method_type == Card:
            charge = Charge.charge(
                amount=amount,
                currency=currency,
                card=payment_method,
                **charge_kwargs,
            )

        else:
            charge = Charge.charge(
                amount=amount,
                currency=currency,
                source={"type": payment_method},
                **charge_kwargs,
            )

        return charge

    def get_success_url(self):
        return self.request.get_full_path()

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs["user"] = self.request.user
        kwargs["amount"] = 100000
        kwargs["currency"] = Currency.THB
        return kwargs

    def get_charge_details(self) -> Dict[int, Currency]:
        """
        Overwrite this method to provide the charge amount and currency.

        Read more on the amount and currency here https://www.omise.co/currency-and-amount

        :returns: Dictionary of charge amount in the smallest unit (int) and the 3-digit currency code. {"amount": int, "currency": str}
        """
        return dict(
            amount=self.request.GET.get("amount", 100000),
            currency=self.request.GET.get("currency", "THB"),
        )

    def get_omise_customer(self) -> Optional[Customer]:
        """
        Get the user to charge. Neccessary for charging with existing card.
        Overwrite this method to provide different way to obtain the customer instance.

        :returns: An instance of Customer if the user is logged in. None otherwise.
        """
        user = self.request.user

        if user.is_authenticated == False:
            return None

        customer, created = Customer.get_or_create(user=self.request.user)
        return customer

    def get_charge_kwargs(self) -> Dict:
        """
        Overwrite this method to add charge parameters.

        :return: A dictionary of charge parameters
        """
        return dict()

    def form_valid(self, form):

        payment_method = form.get_selected_payment_method()

        try:
            charge = self.charge(payment_method=payment_method)
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
