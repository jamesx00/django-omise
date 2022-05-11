import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect

from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, DeleteView, View

from django.http import JsonResponse

from .forms import AddCardForm
from .models.core import Customer, Card, Charge
from .models.event import Event
from .models.choices import ChargeStatus
from .omise import omise

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
        charge = Charge.update_or_create_from_omise_charge(charge=omise_charge)

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


class PaymentMethodDeleteView(LoginRequiredMixin, DeleteView):

    model = Card
    success_message = _("A card has been deleted.")
    success_url = reverse_lazy("django_omise:manage_payment_methods")

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

    def delete(self, *args, **kwargs):

        messages.success(self.request, self.success_message)

        card = self.get_object()
        card.deleted = True
        card.save()

        return redirect(self.success_url)

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
