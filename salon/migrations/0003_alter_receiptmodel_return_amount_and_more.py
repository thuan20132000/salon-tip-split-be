# Generated by Django 5.1.4 on 2024-12-29 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salon', '0002_receiptmodel_staffreceipt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receiptmodel',
            name='return_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='receiptmodel',
            name='sub_total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='receiptmodel',
            name='tip_total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
    ]
