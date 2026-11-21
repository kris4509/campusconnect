from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "provider", "amount", "status", "mpesa_receipt", "created_at")
    list_filter = ("status", "provider")
    search_fields = ("booking__reference", "mpesa_receipt", "phone_number")
    readonly_fields = ("callback_payload", "created_at", "updated_at")
