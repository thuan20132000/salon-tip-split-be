from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import (
    Staff,
    ReceiptModel,
    StaffReceipt,
    Salon
)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email',
                    'phone', 'hire_date', 'is_active', 'salon')
    list_filter = ('is_active', 'gender', 'hire_date')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    ordering = ('-hire_date',)
    date_hierarchy = 'hire_date'

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'gender', 'date_of_birth','salon')
        }),
        ('Employment Details', {
            'fields': ('hire_date', 'is_active')
        }),
    )


@admin.register(ReceiptModel)
class ReceiptModelAdmin(admin.ModelAdmin):
    list_display = ('sub_total_amount', 'return_amount', 'tip_total_amount',
                    'payment_method', 'payment_method_price', 'payment_status')
    list_filter = ('payment_status',)
    search_fields = ('payment_method', 'payment_method_price')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'


@admin.register(StaffReceipt)
class StaffReceiptAdmin(admin.ModelAdmin):
    list_display = ('staff', 'receipt', 'created_at')
    list_filter = ('staff', 'receipt')
    search_fields = ('staff', 'receipt')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'email','owner')
    list_filter = ('name', 'address', 'phone', 'email')
    search_fields = ('name', 'address', 'phone', 'email')
    ordering = ('name', 'address', 'phone', 'email')
    date_hierarchy = 'created_at'