# Generated by Django 4.1.4 on 2023-02-25 23:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0028_alter_customer_companyaddress_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="customer", old_name="address", new_name="deliveryAddress",
        ),
    ]
