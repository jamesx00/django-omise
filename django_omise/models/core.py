from .base import OmiseBaseModel
from .choices import Currency, ChargeStatus
from .managers import NotDeletedManager

import uuid

from django_omise.omise import omise
from django_omise.utils import is_omise_object_instances

from django.conf import settings
from django.contrib.auth import get_user_model

from django.db import models

from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _

from typing import TYPE_CHECKING, Optional, Dict

if TYPE_CHECKING:
    User = get_user_model()


class Customer(OmiseBaseModel):

    """
    A card representing Omise Customer object.

    Official documentation: https://www.omise.co/customers-api
    """

    omise_class = omise.Customer

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="omise_customers",
    )

    deleted = models.BooleanField(
        default=False, help_text=_("Whether this customer was deleted.")
    )

    objects = NotDeletedManager()

    def __str__(self) -> str:
        if self.user:
            return f"Omise{self.__class__.__name__}: {str(self.user)}"
        return f"Omise{self.__class__.__name__}: {self.id}"

    def add_card(self, token: omise.Token) -> "Card":
        """
        Add a new card to the user

        :param token: The token retrieved from Omise API.

        :returns: A new card instance.
        """
        omise_customer = omise.Customer.retrieve(self.id)
        omise_customer.update(card=token.id)

        card = token.card

        new_card, created = Card.objects.update_or_create(
            id=card.id,
            livemode=card.livemode,
            defaults={
                "customer": self,
                "last_digits": card.last_digits,
                "bank": card.bank or "",
                "brand": card.brand or "",
                "city": card.city or "",
                "country": card.country or "",
                "expiration_month": card.expiration_month or "",
                "expiration_year": card.expiration_year or "",
                "financing": card.financing or "",
                "deleted": card.deleted,
            },
        )

        return new_card

    def remove_card(self, card: "Card") -> None:
        """
        Remove the card from the customer.

        :param card: The card to be removed.

        :returns: None
        """
        self.cards.filter(id=card.id).delete()

    def charge_with_card(
        self,
        amount: int,
        currency: Currency.choices,
        card: "Card",
        return_uri: str = None,
        metadata: dict = None,
    ) -> "Charge":
        """
        Charge the customer with provided card.

        :returns: An instace of Charge object.
        """
        uid = uuid.uuid4()

        host = settings.OMISE_CHARGE_RETURN_HOST
        if return_uri is None:
            return_uri = f'https://{host}{reverse("django_omise:return_uri", kwargs={"uid": uid})}'

        if metadata is None:
            metadata = {}

        charge = omise.Charge.create(
            customer=self.id,
            card=card.id,
            amount=int(amount),
            currency=currency,
            metadata=metadata,
            return_uri=return_uri,
        )

        return Charge.update_or_create_from_omise_charge(charge=charge, uid=uid)

    @classmethod
    def get_or_create(cls, user: "User") -> "Customer":
        """
        Get or create django_omise customer.o

        :param user: The user model instance to create a customer.
        :returns: A tuple of Customer instance and whether the object is newly created.
        """
        livemode = settings.OMISE_LIVE_MODE

        try:
            return (
                Customer.objects.get(user=user, livemode=livemode, deleted=False),
                False,
            )
        except Customer.DoesNotExist:

            customer_attributes = {}

            if user.email:
                customer_attributes["email"] = user.email

            omise_customer = cls.omise_class.create(**customer_attributes)

            if omise_customer.livemode != livemode:
                raise ValueError(
                    f"The API livemode inconsistent. API livemode: {omise_customer.livemode}. settings.OMISE_LIVE_MODE: {livemode}"
                )

            return (
                Customer.objects.create(
                    id=omise_customer.id,
                    user=user,
                    livemode=omise_customer.livemode,
                ),
                True,
            )


class Card(OmiseBaseModel):
    """
    A class representing Omise's Card object.

    Official documentation: https://www.omise.co/cards-api
    """

    customer = models.ForeignKey(
        Customer,
        blank=True,
        null=True,
        related_name="cards",
        on_delete=models.PROTECT,
    )

    last_digits = models.CharField(max_length=4)
    bank = models.CharField(max_length=255, blank=True)
    brand = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)

    expiration_month = models.CharField(max_length=2, blank=True)
    expiration_year = models.CharField(max_length=4, blank=True)

    financing = models.CharField(max_length=10, blank=True)

    deleted = models.BooleanField(
        default=False, help_text=_("Whethe this card was deleted.")
    )

    objects = NotDeletedManager()

    def __str__(self) -> str:
        return f"Omise{self.__class__.__name__}: {self.last_digits}"


class Charge(OmiseBaseModel):
    """
    A class representing Omise Charge object.

    Official documentation: https://www.omise.co/charges-api
    """

    status = models.CharField(
        max_length=10,
        choices=ChargeStatus.choices,
        help_text=_("Status of this charge."),
    )

    amount = models.IntegerField(
        help_text="Charge amount in the smallest unit of charge currency"
    )
    authorize_uri = models.CharField(
        max_length=255,
        help_text=_("URI for payment authorization (e.g. 3-D Secure)."),
        blank=True,
    )

    authorized = models.BooleanField(
        blank=True, null=True, help_text=_("Whether charge has been authorized.")
    )
    capturable = models.BooleanField(
        blank=True,
        null=True,
        help_text=_("Whether charge is able to be captured (paid)."),
    )
    capture = models.BooleanField(
        blank=True,
        null=True,
        help_text=_("Whether charge is set to be automatically captured (paid)."),
    )

    card = models.ForeignKey(
        Card,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="charges",
        help_text=_("Card that was charged (if card was charged)."),
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
    )

    customer = models.ForeignKey(
        Customer,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="charges",
        help_text=_("Customer associated with charge."),
    )

    description = models.TextField(blank=True)
    disputable = models.BooleanField(blank=True, null=True)

    expired = models.BooleanField(
        blank=True, null=True, help_text=_("Whether this charge has expired.")
    )

    expired_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    failure_code = models.CharField(max_length=255, blank=True)
    failure_message = models.TextField(blank=True)

    fee = models.IntegerField()
    fee_vat = models.IntegerField()

    funding_amount = models.IntegerField(
        blank=True,
        null=True,
        help_text=_(
            "For multi-currency charges, amount after exchange into account funding currency."
        ),
    )

    funding_currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
    )

    interest = models.IntegerField(
        blank=True,
        null=True,
        help_text=_(
            "Interest paid by customer or merchant over the course of an installment term."
        ),
    )

    interest_vat = models.IntegerField(
        blank=True,
        null=True,
        help_text=_("Value-added Tax (VAT) applied to interest."),
    )

    ip = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "IP address provided to Omise at charge creation. May be IPv4 or IPv6."
        ),
    )

    metadata = models.JSONField(
        default=dict, blank=True, help_text=_("Custom metadata for this charge.")
    )

    net = models.IntegerField(
        help_text=_("funding_amount after fees, interest, and VAT deducted.")
    )

    paid = models.BooleanField(help_text=_("Whether charge has been captured (paid)."))
    paid_at = models.DateTimeField(blank=True, null=True)
    refundable = models.BooleanField(
        help_text=_("Whether charge is able to be refunded.")
    )

    refunded_amount = models.IntegerField(
        blank=True,
        null=True,
        help_text=_("Refunded amount in smallest unit of currency."),
    )

    return_uri = models.TextField(
        blank=True,
        help_text=_(
            "URI to which customer is redirected after 3-D Secure card authorization or other redirect-based authorization."
        ),
    )

    reversed = models.BooleanField(
        blank=True,
        null=True,
        help_text=_("Whether charge authorization is able to be reversed."),
    )

    # To be implemented # schedule = models.ForeignKey(Schedule, on_delete=models.PROTECT, )

    source = models.ForeignKey(
        "Source",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="charges",
    )

    voided = models.BooleanField(
        blank=True,
        null=True,
        help_text=_(
            "Whether, in the case of a refund, charge was voided instead. Charges are voided if refund is processed before settlement time."
        ),
    )

    zero_interest_installments = models.BooleanField(
        blank=True,
        null=True,
        help_text=_(
            "Whether merchant absorbs the interest for installment payments; must match value in associated source."
        ),
    )

    @classmethod
    def charge(
        cls,
        amount: int,
        currency: Currency.choices,
        token: Optional[omise.Token] = None,
        card: Optional[Card] = None,
        source: Optional[Dict] = None,
        return_uri: str = None,
        metadata: dict = None,
    ) -> "Charge":
        """
        Charge the customer with provided payment_method.

        :param amount: The amount to charge in the smallest unit.
        :param currency: The currency to charge.
        :param token: The token to charge.
        :param card: The card to charge.
        :param source: The source to charge.
        :param return_uri optional: The return uri.
        :param metadata optional: The charge metadata.
        :returns: An instace of Charge object.
        """
        if [token, card, source].count(None) == 3:
            raise ValueError("At least a token, a card, or a source is required")

        if [token, card, source].count(None) != 2:
            raise ValueError("Only one of token, card, or source must be specified")

        uid = uuid.uuid4()

        host = settings.OMISE_CHARGE_RETURN_HOST
        if return_uri is None:
            return_uri = f'https://{host}{reverse("django_omise:return_uri", kwargs={"uid": uid})}'

        if metadata is None:
            metadata = {}

        charge_details = {}

        if token is not None:
            if type(token) == str:
                charge_details["card"] = token
            else:
                charge_details["card"] = token.id

        if card is not None:
            charge_details["card"] = card.id
            charge_details["customer"] = card.customer.id

        if source is not None:
            charge_details["source"] = source

        charge = omise.Charge.create(
            amount=int(amount),
            currency=currency,
            metadata=metadata,
            return_uri=return_uri,
            **charge_details,
        )

        return cls.update_or_create_from_omise_charge(charge=charge, uid=uid)

    def set_metadata(self, metadata: Optional[Dict] = None) -> "Charge":
        """
        Set the charge's medata both on Omise and the Charge object.

        :params metadata: A dictionary for medatada

        :returns: The charge instance.
        """

        if metadata is None:
            metadata = {}

        charge = omise.Charge.retrieve(self.id)
        charge.update(metadata=metadata)

        self.metadata = metadata
        self.save()

        return self

    @classmethod
    def update_or_create_from_omise_charge(
        cls,
        charge: omise.Charge,
        uid: Optional[uuid.UUID] = None,
    ) -> "Charge":
        """
        Update existing charge or create a new charge from Omise Charge object.

        :param charge: An instance of Omise Charge object
        :param uid: A unique id for this charge. This is not charge id from Omise.

        :returns: An instance of Charge
        """
        charge_fields = cls._meta.get_fields()

        defaults = {}

        for field in charge_fields:
            if field.name == "metadata":
                defaults["metadata"] = getattr(
                    charge,
                    field.name,
                ).__dict__.get("_attributes")
                continue

            if field.name in cls.NON_DEFAULT_FIELDS:
                continue

            if callable(getattr(charge, field.name, None)):
                continue

            if type(field) is models.ForeignKey:
                value = getattr(charge, field.name, None)

                if value is None:
                    defaults[f"{field.name}_id"] = value
                elif type(value) is str:
                    defaults[f"{field.name}_id"] = value
                else:
                    if type(value) == omise.Card:
                        card = value
                        new_card, created = Card.objects.update_or_create(
                            id=card.id,
                            livemode=card.livemode,
                            defaults={
                                "last_digits": card.last_digits,
                                "bank": card.bank or "",
                                "brand": card.brand or "",
                                "city": card.city or "",
                                "country": card.country or "",
                                "expiration_month": card.expiration_month or "",
                                "expiration_year": card.expiration_year or "",
                                "financing": card.financing or "",
                                "deleted": card.deleted,
                            },
                        )

                    if type(value) == omise.Source:
                        source = value
                        new_source = Source.update_or_create_from_omise_source(
                            source=source,
                        )

                    defaults[f"{field.name}_id"] = getattr(charge, field.name).id

                continue

            if is_omise_object_instances(getattr(charge, field.name, None)):
                defaults[f"{field.name}_id"] = getattr(charge, field.name).id
                continue

            if (
                isinstance(field, (models.TextField, models.CharField))
                and getattr(charge, field.name, None) is None
            ):
                defaults[field.name] = ""
                continue

            if (
                getattr(charge, field.name, None) is None
                and field.null == False
                and field.default
            ):
                defaults[field.name] = field.default()
                continue

            defaults[field.name] = getattr(charge, field.name, None)

        charge_object, created = cls.objects.update_or_create(
            pk=charge.id,
            livemode=charge.livemode,
            defaults=defaults,
        )

        if uid:
            charge_object.uid = uid
            charge_object.save()

        return charge_object


class Source(OmiseBaseModel):
    """
    A class representing Omise Source object.

    Official documentation: https://www.omise.co/sources-api
    """

    NON_DEFAULT_FIELDS = OmiseBaseModel.NON_DEFAULT_FIELDS + [
        "charges",
    ]

    amount = models.IntegerField(
        help_text=_("Source amount in smallest unit of source currency")
    )

    bank = models.CharField(max_length=255, blank=True)

    barcode = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Source amount in smallest unit of source currency"),
    )

    charge_status = models.CharField(
        max_length=10,
        choices=ChargeStatus.choices,
        help_text=_("Status of charge created using this source (if any)"),
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
    )

    email = models.CharField(
        max_length=255, blank=True, help_text=_("The payer's email")
    )

    flow = models.CharField(
        max_length=50,
        help_text=_(
            "The payment flow payers need to go through to complete the payment. One of redirect, offline, or app_redirect"
        ),
    )

    installment_term = models.IntegerField(
        blank=True, null=True, help_text=_("Installment term in months")
    )
    mobile_number = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=255, blank=True, help_text=_("Payer's name"))
    phone_number = models.CharField(max_length=50, blank=True)
    platform_type = models.CharField(
        max_length=50,
        blank=True,
        help_text=_(
            "Platform from which payer is making a payment. One of WEB, IOS, or ANDROID"
        ),
    )

    receipt_amount = models.IntegerField(blank=True, null=True)
    store_id = models.CharField(max_length=255, blank=True)
    store_name = models.CharField(max_length=255, blank=True)
    terminal_id = models.CharField(max_length=255, blank=True)

    type = models.CharField(max_length=255)

    zero_interest_installments = models.BooleanField(blank=True, null=True)

    @classmethod
    def update_or_create_from_omise_source(
        cls,
        source: omise.Source,
    ) -> "Source":
        fields = cls._meta.get_fields()

        defaults = {}

        for field in fields:

            if field.name in cls.NON_DEFAULT_FIELDS:
                continue

            if callable(getattr(source, field.name, None)):
                continue

            if type(field) is models.ForeignKey:
                value = getattr(source, field.name, None)

                if value is None:
                    defaults[f"{field.name}_id"] = value
                elif type(value) is str:
                    defaults[f"{field.name}_id"] = value
                else:
                    defaults[f"{field.name}_id"] = getattr(source, field.name).id

                continue

            if is_omise_object_instances(getattr(source, field.name, None)):
                defaults[f"{field.name}_id"] = getattr(source, field.name).id
                continue

            if (
                isinstance(field, (models.TextField, models.CharField))
                and getattr(source, field.name, None) is None
            ):
                defaults[field.name] = ""
                continue

            if (
                getattr(source, field.name, None) is None
                and field.null == False
                and field.default
            ):
                defaults[field.name] = field.default()
                continue

            defaults[field.name] = getattr(source, field.name, None)

        new_source, created = cls.objects.update_or_create(
            pk=source.id,
            livemode=source.livemode,
            defaults=defaults,
        )

        return new_source
