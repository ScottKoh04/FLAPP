# Generated by Django 4.1.4 on 2023-02-06 02:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0004_invoice"),
    ]

    operations = [
        migrations.DeleteModel(name="Invoice",),
    ]