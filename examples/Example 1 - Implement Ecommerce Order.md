# Example 1

In this example, let's say we have another simple ecommerce application with a model **_Product, Cart, CartItem, Order, OrderItem_** (See class definitions at the bottom of the example). You can create a checkout view with the built-in mixin as below:

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View

from django_omise.mixins import CheckoutMixin

class CheckoutView(LoginRequiredMixin, CheckoutMixin):
    template_name = "my_app/checkout.html"

    def get_charge_details(self):
        cart = self.request.user.cart
        return {
            "amount": cart.total * 100,
            "currency": cart.currency,
        }

    def process_charge_and_form(self, charge, form):
        # The charge provided for this method is a Charge object from our database, not from Omise's server.

        address = form.cleaned_data["address"]

        if charge.status in [ChargeStatus.SUCCESSFUL, ChargeStatus.PENDING]:

            order = create_or_from_cart(cart=cart)

            order.omise_charge = charge
            order.save()

            # success_url is redirected to when the charge status is successful right away, not when the charge status is pending from 3DS checkout.
            self.success_url = order.get_absolute_url()

            # Setting metadata successful_url and failed_url
            charge.set_metadata(
                metadata={
                    "successful_url": self.request.build_absolute_uri(
                        order.get_absolute_url()
                    ),
                    "failed_url": self.request.build_absolute_uri(
                        reverse(
                            "my_app:revert_failed_order", kwargs={"pk": order.pk}
                        ) # Redirect to RevertFailedOrderView defined below.
                    ),
                }
            )


class RevertFailedOrderView(View):
    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        order.revert_to_cart()
        return redirect(reverse("ecommerce:checkout"))

```

## Class Definitions

```python
from django.db import models
from django_omise.models.core import Charge
from django_omise.models.choices import Currency

class Product(models.Model):

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=4)
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.THB
    )


class Order(EcommerceBaseModel):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        blank=True,
        null=True,
    )

    omise_charge = models.ForeignKey(
        Charge, on_delete=models.PROTECT, blank=True, null=True
    )

    def get_absolute_url(self):
        return reverse_lazy("my_app:order_detail", kwargs={"pk": self.pk})


class OrderItem(EcommerceBaseModel):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()

    price_at_purchase = models.DecimalField(
        max_digits=12,
        decimal_places=4,
    )

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="cart",
        primary_key=True,
        on_delete=models.CASCADE,
    )

    @property
    def total(self) -> float:
        """The total amount of the items in the cart."""
        if self.items.count() > 0:
            return sum([item.total for item in self.items.all()])
        return 0

    @property
    def currency(self) -> str:
        """The currency of the first item in the cart."""
        if self.items.count() > 0:
            return self.items.first().currency
        return None

    def clean(self):
        """Validate that all the items in the cart are of the same currrency."""


class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        ProductPrice,
        on_delete=models.CASCADE,
    )
    qty = models.PositiveIntegerField(default=1)

    @property
    def total(self) -> float:
        return self.product.price * self.qty

    @property
    def currency(self) -> str:
        return self.product.currency

    class Meta:
        unique_together = ["cart", "product"]

```
