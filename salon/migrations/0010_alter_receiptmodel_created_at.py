# Generated by Django 5.1.4 on 2025-01-08 03:15

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salon', '0009_receiptmodel_salon_staff_salon_alter_salon_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receiptmodel',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
