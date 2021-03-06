# Generated by Django 3.2.13 on 2022-05-22 00:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_omise", "0002_alter_chargeschedule_card"),
    ]

    operations = [
        migrations.AlterField(
            model_name="source",
            name="type",
            field=models.CharField(
                choices=[
                    ("truemoney", "TrueMoney Wallet"),
                    ("internet_banking_bay", "Krungsri Bank"),
                    ("internet_banking_bbl", "Bangkok Bank"),
                    ("internet_banking_ktb", "Krungthai Bank"),
                    ("internet_banking_scb", "SCB Bank"),
                    ("promptpay", "Promptpay"),
                    ("rabbit_linepay", "Rabbit LINE Pay"),
                ],
                max_length=255,
            ),
        ),
    ]
