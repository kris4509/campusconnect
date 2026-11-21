from django.contrib import admin

from .models import Booking, Ticket


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("reference", "event", "student", "quantity", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("reference", "student__email", "event__title")
    readonly_fields = ("reference", "created_at", "updated_at")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("reference", "booking", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("reference", "booking__reference")
    readonly_fields = ("reference", "created_at")
