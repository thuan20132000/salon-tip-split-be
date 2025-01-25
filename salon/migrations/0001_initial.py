# Generated by Django 5.1.4 on 2025-01-25 04:41

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Salon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('address', models.TextField(blank=True, null=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Salon',
                'verbose_name_plural': 'Salons',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ReceiptModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sub_total_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('return_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('tip_total_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('payment_method', models.CharField(blank=True, max_length=100, null=True)),
                ('payment_method_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('payment_status', models.CharField(choices=[('PENDING', 'Pending'), ('PAID', 'Paid')], default='PENDING', max_length=20)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('custom_discount', models.FloatField(default=0)),
                ('bonus_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('salon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='salon.salon')),
            ],
            options={
                'verbose_name': 'Receipt',
                'verbose_name_plural': 'Receipts',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=True)),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('phone', models.CharField(max_length=15)),
                ('address', models.TextField(blank=True, null=True)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], default='M', max_length=1)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('hire_date', models.DateField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('commission_rate', models.FloatField(blank=True, default=0, null=True)),
                ('role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='role', to='salon.role')),
                ('salon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='salon.salon')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staff', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Staff',
                'verbose_name_plural': 'Staff',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='StaffReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tip_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('service_name', models.CharField(blank=True, max_length=100, null=True)),
                ('discount_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('discount_percent', models.FloatField(default=0)),
                ('status', models.BooleanField(default=True, help_text='Check this box if the service is completed')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('receipt', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staff_receipts', to='salon.receiptmodel')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='salon.staff')),
            ],
            options={
                'verbose_name': 'Staff Receipt',
                'verbose_name_plural': 'Staff Receipts',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserDeviceModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_id', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('device_type', models.CharField(blank=True, max_length=20, null=True)),
                ('active', models.BooleanField(default=True)),
                ('last_used', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='devices', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Device',
                'verbose_name_plural': 'User Devices',
                'ordering': ['-created_at'],
            },
        ),
    ]
