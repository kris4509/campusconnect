from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("student/", views.student_dashboard, name="student"),
    path("organizer/", views.organizer_dashboard, name="organizer"),
    path("admin/", views.admin_dashboard, name="admin"),
    path("admin/events/", views.event_approvals, name="event_approvals"),
    path("admin/events/<int:pk>/<str:action>/", views.event_approval_action, name="event_approval_action"),
    path("admin/users/", views.user_management, name="users"),
    path("admin/bookings/", views.booking_management, name="bookings"),
    path("admin/payments/", views.payment_management, name="payments"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
]
