from django.urls import path

from . import views

app_name = "events"

urlpatterns = [
    path("", views.event_list, name="list"),
    path("<int:pk>/", views.event_detail, name="detail"),
    path("create/", views.event_create, name="create"),
    path("<int:pk>/edit/", views.event_edit, name="edit"),
    path("<int:pk>/attendees/", views.event_attendees, name="attendees"),
]
