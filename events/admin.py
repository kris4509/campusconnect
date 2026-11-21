from django.contrib import admin

from .models import Event, EventCategory


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "organizer", "event_date", "ticket_price", "publication_status", "is_approved")
    list_filter = ("publication_status", "is_approved", "category", "event_date")
    search_fields = ("title", "description", "venue")
    date_hierarchy = "event_date"
    readonly_fields = ("created_at", "updated_at")
