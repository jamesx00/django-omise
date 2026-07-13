# django-omise Django + Omise

![Test](https://github.com/jamesx00/django-omise/actions/workflows/tests.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/jamesx00/django-omise/badge.svg?branch=master)](https://coveralls.io/github/jamesx00/django-omise?branch=master)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/jamesx00/django-omise/issues)

Django models for Omise. Currently, we support the following features:

- Creating a customer
- Allowing customer to add/delete credit/debit cards
- Collect payments with new card with the option to keep the card
- Collect payments with saved cards
- Collect payments with [Internet Banking](https://www.omise.co/internet-banking)
- Collect payments with [TrueMoney Wallet](https://www.omise.co/truemoney-wallet)
- Collect payments with [Promptpay](https://www.omise.co/promptpay)
- Collect payments with [Rabbit LINE Pay](https://www.omise.co/rabbit-linepay)
- Webhook handler, saving raw data as an Event object and update related objects, currently supporting

  - Customer
  - Card
  - Charge
  - Source
  - Refund
  - Schedule
  - Scheduled Charge
  - Schedule Occurrence

- 3DS pending charges handling

See the [roadmap](#roadmap-and-contributions) for the plan of this project. Contributions are welcome!

### Upgrading

---

**0.3.0 (breaking change)**

`Charge.charge()` (and `Customer.charge_with_card()`) no longer silently build a broken
`return_uri` when `OMISE_CHARGE_RETURN_HOST` is unset. Behavior now:

- If you use `CheckoutMixin` / `CheckoutWithCardsMixin`, no change needed — the request is
  forwarded automatically.
- If you call `Charge.charge()` or `customer.charge_with_card()` manually outside a request
  (e.g. management command, background job) and don't pass `return_uri` or `request`, and
  `OMISE_CHARGE_RETURN_HOST` isn't set, this now raises `ValueError` instead of producing an
  invalid `return_uri`. Fix by passing `request=` (if available), `return_uri=` directly, or
  setting `OMISE_CHARGE_RETURN_HOST`.

### Quick start

---

1. Add "django_omise" to your INSTALLED_APPS setting like this:

```
    INSTALLED_APPS = [
        ...
        "django_omise",
    ]
```

2. Include the django_omise URLconf in your project urls.py like this:

```
    path("payments/", include("django_omise.urls")),
```

3. Add Omise keys and operating mode in settings.py:

```python
OMISE_PUBLIC_KEY = xxxx
OMISE_SECRET_KEY = xxxx
OMISE_LIVE_MODE = True | False

# Optional. The default payment method is credit/debit card only.
# You must specify additional payment methods.
OMISE_PAYMENT_METHODS = [
    "card",
    "internet_banking", # Internet Banking
    "truemoney_wallet", # TrueMoney Wallet
    "promptpay", # Promptpay
    "rabbit_linepay", # Rabbit LINE Pay
]
```

By default, `Charge.charge()` builds the Omise `return_uri` from the host of
the current request (via `CheckoutMixin`/`CheckoutWithCardsMixin`, or by
passing `request=` yourself), so each site in a multi-site deployment
returns to its own host automatically.

```python
# Optional. Overrides the request-derived host, e.g. when running behind a
# proxy that reports the wrong host, or when charging outside of a request
# (management commands, background jobs) without passing return_uri directly.
OMISE_CHARGE_RETURN_HOST = localhost:8000
```

4. Run `python manage.py migrate` to create the Omise models.

5. Add Omise endpoint webhook url `https://www.your-own-domain.com/payments/webhook/`

### Basic usage

---

1. Create an Omise customer from User:

   ```python
   from django.contrib.auth import get_user_model
   from django_omise.models.core import Customer

   User = get_user_model()
   user = User.objects.first()
   customer = Customer.get_or_create(user=user)
   ```

2. Add card to Customer

   2.1 With the built-in view (Recommended)

   We have built a basic card collecting view where logged in users can add and remove their cards. Run Django server and visit _/payments/payment_methods/_ to see it in action. You could override the template used in the view by creating a new template in your project's directory _/templates/django_omise/manage_payment_methods.html_.

   2.2 Manually

   ```python
   from django_omise.models.core import Customer
   from django_omise.omise import omise

   omise_token = omise.Token.retrieve(token_id)
   Customer.objects.live().first().add_card(token=omise_token)
   ```

3. Charge a customer (Currently supporting new/saved cards, [Internet Banking](https://www.omise.co/internet-banking), [TrueMoney Wallet](https://www.omise.co/truemoney-wallet), [Promptpay](https://www.omise.co/promptpay))

   3.1 With the build-in mixin

   This package comes with a built-in mixin, with which you can create a class-based-view and write a few methods to charge a customer. See below for an example or see [Example 1](./examples/):

   ```python
   from django.contrib.auth.mixins import LoginRequiredMixin
   from django_omise.mixins import CheckoutMixin
   from django_omise.models.choices import Currency

   # Your own class-based-view
   class CheckoutView(LoginRequiredMixin, CheckoutMixin):

       template_name = "yourapp/template.html"
       success_url = ...

       def get_charge_details(self):
           return {
               "amount": 100000,
               "currency": Currency.THB,
           }

       def process_charge_and_form(self, charge, form):
           if charge.status in [ChargeStatus.SUCCESSFUL, ChargeStatus.PENDING]:
               # Create new order and attach a charge object
               # And handle form data
               handle_form_data(form.cleaned_data)
   ```

   3.2 Manually

   ```python
   from django_omise.models.choices import Currency, ChargeStatus
   from django_omise.models.core import Customer

   customer = Customer.objects.first()
   card = customer.cards.live().first()

   # `request` is required unless OMISE_CHARGE_RETURN_HOST is set or you pass
   # return_uri= directly. See "Upgrading" above.
   charge = customer.charge_with_card(
       amount=100000,
       currency=Currency.THB,
       card=card,
       request=request,
   )

   if charge.status == ChargeStatus.SUCCESSFUL:
       # Do something
   elif charge.status == ChargeStatus.FAILED:
       # Do something else
   ```

4. Create a charge schedule for a customer:

At the moment, you can create a new schedule for a customer manually by calling the method create_schedule from a Custoemr object. See below for an example:

```python
import datetime
from django_omise.models.choices import Currency
from django_omise.models.core import Customer

customer = Customer.objects.first()
card = customer.default_card

customer.create_schedule(
    amount=100000,
    currency=Currency.THB,
    card=card,
    every=1,
    period="month",
    start_date=datetime.date(year=2022, month=5, day=22),
    end_date=datetime.date(year=2032, month=5, day=22),
    on={
        'days_of_month': [22],
    },
    description="Monthly subscription",
)
```

### Roadmap and contributions

---

Here are our immediate plans for this package, and more will be added! All contributions are welcome. I am new to publishing a public package, so if you have any recommendations, please feel free to create an issue on this repository or feel free to send me an email at siwatjames@gmail.com.

Omise Features

- [x] Handle refunds API
- Handle webhook events and update related objects
- Create charge with Sources
  - [x] Internet banking
  - [x] TrueMoney Wallet
  - [x] Promptpay
  - [x] Rabbit LINE Pay
  - [ ] Installment
- Schedule
  - [x] Scheduled Charges
  - [ ] Scheduled Transfer

Others

- Implement tests
- Add documentations

### Contributing

---

This project uses [uv](https://docs.astral.sh/uv/) for dependency management. Install uv, then:

```shell
git clone git@github.com:jamesx00/django-omise.git
cd django-omise
uv sync --group dev
```

This creates a `.venv` and installs the package plus dev dependencies (pytest, black, poethepoet, etc.) pinned in `uv.lock`.

Tests need a Postgres database. Start one with docker-compose:

```shell
docker-compose up -d
```

Then run the test suite with one of the [poe](https://github.com/nat-n/poethepoet) tasks defined in `pyproject.toml`:

```shell
uv run poe test                # pytest --verbose
uv run poe test_coverage       # coverage run run_tests.py
uv run poe test_coverage_html  # pytest with HTML coverage report
uv run poe test_coverage_term  # pytest with terminal coverage report
```

Or invoke pytest/coverage directly inside the uv environment:

```shell
uv run pytest [path_to_file] [--verbose -s --cov-report=html --cov=.]
uv run coverage run run_tests.py
```

Format code with black before submitting a PR:

```shell
uv run black .
```

Please open an issue or PR against `master` — see [Roadmap and contributions](#roadmap-and-contributions) for areas that need help.
