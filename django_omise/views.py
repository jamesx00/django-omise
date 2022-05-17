import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect

from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, UpdateView, View

from django.http import JsonResponse

from .forms import AddCardForm
from .mixins import CheckoutMixin
from .models.core import Customer, Card, Charge
from .models.event import Event
from .models.choices import ChargeStatus, Currency
from .omise import omise

from typing import Dict

# Create your views here.
@csrf_exempt
def omise_webhook_view(request):

    try:
        event_data = json.loads(request.body)
    except json.decoder.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": "The data could not be parsed with JSON"},
            status=500,
        )

    try:
        omise_event = omise.Event.retrieve(event_data.get("id"))
    except omise.errors.NotFoundError:
        return JsonResponse(
            {
                "success": False,
                "message": f"Could not find the event with the id {event_data.get('id')}.",
            },
            status=404,
        )

    Event.objects.update_or_create(
        id=omise_event.id,
        livemode=omise_event.livemode,
        defaults={
            "event_type": omise_event.key,
            "date_created": omise_event.created_at,
            "data": event_data,
        },
    )

    response = {}

    return JsonResponse(response, status=200)


class OmiseReturnURIView(View):

    redirect_url = "/"

    def get_redirect_url(self, charge):

        if charge.status == ChargeStatus.SUCCESSFUL:
            return self.request.GET.get(
                "successful_url",
                charge.metadata.get("successful_url", self.redirect_url),
            )

        elif charge.status == ChargeStatus.FAILED:
            return self.request.GET.get(
                "failed_url", charge.metadata.get("failed_url", self.redirect_url)
            )

        return self.redirect_url

    def get(self, request, uid):

        charge = Charge.objects.get(uid=uid)
        omise_charge = omise.Charge.retrieve(charge.id)
        charge = Charge.update_or_create_from_omise_object(omise_object=omise_charge)

        if charge.status == ChargeStatus.SUCCESSFUL:
            messages.success(request, _("Payment successful"))

        if charge.status == ChargeStatus.FAILED:
            messages.warning(request, charge.failure_message)

        return redirect(self.get_redirect_url(charge))


class ManagePaymentMethodsView(LoginRequiredMixin, SuccessMessageMixin, FormView):

    form_class = AddCardForm
    template_name = "django_omise/manage_payment_methods.html"
    success_message = _("A new payment method has been added.")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["customer"] = self.get_customer()
        return context

    def get_customer(self) -> Customer:
        """
        Get the customer to add the card to.

        Overwrite this method to change how the customer is retrieved.

        :returns: A Customer instance
        """
        customer, created = Customer.get_or_create(
            user=self.request.user,
        )

        return customer

    def form_valid(self, form):
        form.add_card_to_user(self.get_customer())
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return self.request.GET.get(
            "next", reverse_lazy("django_omise:manage_payment_methods")
        )


class PaymentMethodDeleteView(LoginRequiredMixin, UpdateView):

    model = Card
    fields = [
        "deleted",
    ]
    success_message = _("A card has been deleted.")
    success_url = reverse_lazy("django_omise:manage_payment_methods")
    template_name = "django_omise/card_confirm_delete.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["customer"] = self.get_customer()
        return context

    def get_customer(self) -> Customer:
        """
        Get the customer to add the card to.

        Overwrite this method to change how the customer is retrieved.

        :returns: A Customer instance
        """
        customer, created = Customer.get_or_create(
            user=self.request.user,
        )
        return customer

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.deleted = True

        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def post(self, *args, **kwargs):

        object = self.get_object()
        if object.customer != self.get_customer():
            return redirect(reverse("django_omise:manage_payment_methods"))

        return super().post(*args, **kwargs)

    def get(self, *args, **kwargs):

        object = self.get_object()
        if object.customer != self.get_customer():
            return redirect(reverse("django_omise:manage_payment_methods"))

        return super().get(*args, **kwargs)


class CheckoutView(CheckoutMixin):
    template_name = "django_omise/checkout.html"

    def get_success_url(self, *args, **kwargs):
        return self.request.get_full_path()

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

    def get_charge_kwargs(self) -> Dict:
        """
        Overwrite this method to add charge parameters.

        :return: A dictionary of charge parameters
        """
        return dict(
            metadata=dict(
                successful_url=self.request.get_full_path(),
                failed_url=self.request.get_full_path(),
            )
        )
