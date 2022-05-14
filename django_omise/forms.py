from django import forms
from django.conf import settings

from .omise import omise

from django.utils.translation import gettext_lazy as _

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models.core import Customer


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
