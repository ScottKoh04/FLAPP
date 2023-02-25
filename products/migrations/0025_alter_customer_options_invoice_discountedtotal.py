# Generated by Django 4.1.4 on 2023-02-25 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0024_order_discount"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="customer", options={"ordering": ["firstname"]},
        ),
        migrations.AddField(
            model_name="invoice",
            name="discountedTotal",
            field=models.FloatField(null=True),
        ),
    ]