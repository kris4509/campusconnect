from django.urls import path

from . import views

app_name = "bookings"

urlpatterns = [
    path("", views.booking_list, name="list"),
    path("create/<int:event_id>/", views.create, name="create"),
    path("<int:pk>/cancel/", views.cancel, name="cancel"),
    path("tickets/", views.tickets, name="tickets"),
    path("tickets/<int:pk>/", views.ticket_detail, name="ticket_detail"),
]
