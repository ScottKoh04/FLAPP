# Generated by Django 4.1.4 on 2023-02-19 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0017_customer_postcode"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="postcode",
            field=models.IntegerField(null=True),
        ),
    ]
