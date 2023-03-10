# Generated by Django 4.1.4 on 2022-12-27 09:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("firstname", models.CharField(max_length=50, null=True)),
                ("lastname", models.CharField(max_length=50, null=True)),
                ("phone", models.IntegerField(null=True)),
                ("email", models.CharField(max_length=50, null=True)),
                ("creditBalance", models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Tier",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tierValue", models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("firstname", models.CharField(max_length=50, null=True)),
                ("lastname", models.CharField(max_length=50, null=True)),
                ("phone", models.IntegerField(null=True)),
                ("email", models.CharField(max_length=50, null=True)),
                ("username", models.CharField(max_length=50, null=True)),
                ("password", models.CharField(max_length=50, null=True)),
                ("accountType", models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("productName", models.CharField(max_length=20, null=True)),
                ("grade", models.CharField(max_length=5, null=True)),
                ("unitPrice", models.FloatField(null=True)),
                (
                    "tier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="products.tier"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("transactionTime", models.DateTimeField(auto_now_add=True)),
                ("weight", models.IntegerField(null=True)),
                ("subtotal", models.FloatField(null=True)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="products.customer",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="products.product",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="customer",
            name="tier",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="products.tier"
            ),
        ),
    ]
