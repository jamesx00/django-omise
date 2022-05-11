# django-omise Django + Omise

Django models for Omise

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
OMISE_CHARGE_RETURN_HOST = localhost:8000
```

4. Run `python manage.py migrate` to create the Omise models.

5. Add Omise endpoint webhook url `https://host.com/payments/webhook/`
