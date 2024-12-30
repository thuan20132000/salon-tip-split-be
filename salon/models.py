from django.db import models
from django.utils import timezone

# Create your models here.


class Staff(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, default='M')
    date_of_birth = models.DateField(blank=True, null=True)
    hire_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Staff"
        verbose_name_plural = "Staff"
        ordering = ['-created_at']


class ReceiptModel(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
    )

    sub_total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    return_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    tip_total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    payment_method = models.CharField(max_length=100, blank=True, null=True)
    payment_method_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        print(self.staff_receipts)
        return f"Receipt_id {self.id}"

    class Meta:
        verbose_name = "Receipt"
        verbose_name_plural = "Receipts"
        ordering = ['-created_at']


class StaffReceipt(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    receipt = models.ForeignKey(ReceiptModel, on_delete=models.CASCADE,
                                null=True, blank=True, related_name='staff_receipts')
    service_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    tip_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    service_name = models.CharField(max_length=100, blank=True, null=True)

    status = models.BooleanField(
        default=True, help_text="Check this box if the service is completed"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Receipt for {self.staff.first_name} {self.staff.last_name}"

    class Meta:
        verbose_name = "Staff Receipt"
        verbose_name_plural = "Staff Receipts"
        ordering = ['-created_at']
