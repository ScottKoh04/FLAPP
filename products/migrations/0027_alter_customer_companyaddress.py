# Generated by Django 4.1.4 on 2023-02-25 16:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0026_remove_invoice_summary_alter_customer_tier"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="companyAddress",
            field=models.CharField(
                max_length=30,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(regex="^\\d{3}\\d{3}\\d{4}$")
                ],
            ),
        ),
    ]
