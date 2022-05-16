from django import forms
from django.conf import settings

from .models.core import Customer, Card
from .models.choices import Currency
from .omise import omise

from django.utils.translation import gettext_lazy as _

from typing import List


class AddCardForm(forms.Form):

    omise_token = forms.CharField(
        widget=forms.HiddenInput,
    )

    omise_public_key = forms.CharField(
        widget=forms.HiddenInput,
        disabled=True,
        initial=settings.OMISE_PUBLIC_KEY,
    )

    card_number = forms.CharField(
        required=False,
    )

    name_on_card = forms.CharField(
        required=False,
    )

    expiration_month = forms.CharField(
        required=False,
    )

    expiration_year = forms.CharField(
        required=False,
    )

    security_number = forms.CharField(
        required=False,
    )

    class Media:
        js = (
            "django_omise/js/jquery.min.js",
            "django_omise/js/jquery.payments.js",
            "django_omise/js/omise.js",
            "django_omise/js/add_card.js",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["card_number"].widget.attrs["placeholder"] = "1234 1234 1234 1234"
        self.fields["name_on_card"].widget.attrs["placeholder"] = "John Doe"
        self.fields["expiration_month"].widget.attrs["placeholder"] = "1-12"
        self.fields["expiration_year"].widget.attrs["placeholder"] = "2030"
        self.fields["security_number"].widget.attrs["placeholder"] = "***"

    def clean_omise_token(self) -> omise.Token:
        """
        Check that the credit card token is valid.
        """
        try:
            omise_token = omise.Token.retrieve(self.cleaned_data["omise_token"])
        except omise.errors.NotFoundError:
            raise forms.ValidationError(
                _("Error processing the card. Please try again.")
            )

        return omise_token

    def add_card_to_user(self, customer: "Customer"):
        """
        Add the new card to the user.

        :params customer: The customer instance

        :returns None:
        """
        customer.add_card(self.cleaned_data["omise_token"])


class CheckoutWithCardsForm(forms.Form):

    card = forms.ModelChoiceField(queryset=None, widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):

        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        self.user = user

        if user is None:
            return

        if not user.is_authenticated:
            return

        self.omise_customer = self.user.extension.omise_customer
        self.fields["card"].queryset = self.omise_customer.cards.live()


class PayWithNewCardForm(forms.Form):

    omise_token = forms.CharField(
        widget=forms.HiddenInput,
        required=False,
    )

    card_number = forms.CharField(
        required=False,
    )

    name_on_card = forms.CharField(
        required=False,
    )

    expiration_month = forms.CharField(
        required=False,
    )

    expiration_year = forms.CharField(
        required=False,
    )

    security_number = forms.CharField(
        required=False,
    )

    keep_card = forms.BooleanField(initial=False, required=False)

    class Media:
        js = (
            "django_omise/js/jquery.min.js",
            "django_omise/js/jquery.payments.js",
            "django_omise/js/omise.js",
            "django_omise/js/checkout.js",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["card_number"].widget.attrs["placeholder"] = "1234 1234 1234 1234"
        self.fields["name_on_card"].widget.attrs["placeholder"] = "John Doe"
        self.fields["expiration_month"].widget.attrs["placeholder"] = "1-12"
        self.fields["expiration_year"].widget.attrs["placeholder"] = "2030"
        self.fields["security_number"].widget.attrs["placeholder"] = "***"

        self.fields["card_number"].initial = "4111 1111 1111 1111"
        self.fields["name_on_card"].initial = "James"
        self.fields["expiration_month"].initial = "10"
        self.fields["expiration_year"].initial = "2030"
        self.fields["security_number"].initial = "123"

    def clean_omise_token(self) -> omise.Token:
        """
        Check that the credit card token is valid.
        """
        if not self.cleaned_data["omise_token"]:
            return None

        try:
            omise_token = omise.Token.retrieve(self.cleaned_data["omise_token"])
        except omise.errors.NotFoundError:
            raise forms.ValidationError(
                _("Error processing the card. Please try again.")
            )

        return omise_token

    def add_card_to_user(self, customer: "Customer"):
        """
        Add the new card to the user.

        :params customer: The customer instance

        :returns None:
        """
        card = customer.add_card(self.cleaned_data["omise_token"])
        return card


class PayWithExistingCardForm(forms.Form):

    card = forms.ModelChoiceField(
        queryset=None, widget=forms.RadioSelect, required=False
    )


class PayWithInternetBankingForm(forms.Form):

    bank = forms.ChoiceField(
        choices=(
            ("internet_banking_bay", _("Krungsri Bank")),
            ("internet_banking_bbl", _("Bangkok Bank")),
            ("internet_banking_ktb", _("Krungthai Bank")),
            ("internet_banking_scb", _("SCB Bank")),
        ),
        widget=forms.RadioSelect,
        required=False,
        initial="internet_banking_bay",
    )


class CheckoutForm(
    PayWithExistingCardForm,
    PayWithNewCardForm,
    PayWithInternetBankingForm,
):

    payment_method = forms.ChoiceField(
        choices=(), required=True, widget=forms.RadioSelect
    )

    omise_public_key = forms.CharField(
        widget=forms.HiddenInput,
        disabled=True,
        initial=settings.OMISE_PUBLIC_KEY,
    )

    def __init__(self, user, amount: int, currency: Currency, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user
        self.amount = amount
        self.currency = currency

        payment_methods = {
            "old_card": _("Pay with your card"),
            "new_card": _("Pay with a new card"),
            "internet_banking": _("Internet banking"),
        }

        if user is None or user.is_authenticated == False:

            self.fields["payment_method"].initial = "new_card"

            del self.fields["keep_card"]
            del self.fields["card"]

            del payment_methods["old_card"]

        else:

            self.omise_customer, created = Customer.get_or_create(user=user)

            if self.omise_customer.cards.live().exists():

                self.fields["payment_method"].initial = "old_card"
                self.fields["card"].queryset = self.omise_customer.cards.live()
                self.fields["card"].initial = self.omise_customer.cards.live().first()

            else:

                self.fields["payment_method"].initial = "new_card"
                del payment_methods["old_card"]
                del self.fields["card"]

        payment_method_choices = []
        for key, value in payment_methods.items():
            payment_method_choices.append((key, value))
        self.fields["payment_method"].choices = payment_method_choices

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data["payment_method"]
        omise_token = cleaned_data.get("omise_token")
        card = cleaned_data.get("card")
        bank = cleaned_data.get("bank")

        if payment_method == "new_card" and omise_token is None:
            raise forms.ValidationError(
                {"card_number": _("You need to provide a new card details")}
            )

        if payment_method == "old_card" and card is None:
            raise forms.ValidationError(
                {"card": _("You need to select at least one card")}
            )

        if payment_method == "internet_banking" and not bank:
            raise forms.ValidationError(
                {"bank": _("You need to select at least one bank")}
            )

    def get_selected_payment_method(self) -> Card:
        payment_method = self.cleaned_data["payment_method"]

        if payment_method == "new_card":

            if self.cleaned_data.get("keep_card", None) == True:
                card = self.add_card_to_user()
                return card

            return self.cleaned_data["omise_token"]

        if payment_method == "old_card":
            return self.cleaned_data["card"]

        if payment_method == "internet_banking":
            return self.cleaned_data["bank"]

    def add_card_to_user(self) -> Card:
        """
        Add the new card to the user.

        :params customer: The customer instance

        :returns: The new Card instance
        """
        return self.omise_customer.add_card(self.cleaned_data["omise_token"])

    @property
    def new_card_fields(self) -> List[forms.fields.Field]:

        new_card_field_names = [
            "omise_token",
            "card_number",
            "name_on_card",
            "expiration_year",
            "expiration_month",
            "security_number",
            "keep_card",
        ]

        return [
            field
            for field in self
            if field.name in new_card_field_names and not field.is_hidden
        ]
