# Generated by Django 5.1.4 on 2025-01-08 03:16

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salon', '0010_alter_receiptmodel_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receiptmodel',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
