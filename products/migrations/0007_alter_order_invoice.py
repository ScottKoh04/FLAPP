# Generated by Django 4.1.4 on 2023-02-08 10:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0006_invoice_order_invoice"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="invoice",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="products.invoice",
            ),
        ),
    ]