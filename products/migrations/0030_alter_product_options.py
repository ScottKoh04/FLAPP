# Generated by Django 4.1.4 on 2023-02-28 22:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0029_rename_address_customer_deliveryaddress"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="product", options={"ordering": ["productName", "-unitPrice"]},
        ),
    ]
