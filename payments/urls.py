from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("callback/", views.payment_callback, name="callback"),
    path("pay/<int:booking_id>/", views.pay, name="pay"),
    path("status/<int:payment_id>/", views.status, name="status"),
    path("status/<int:payment_id>/check/", views.status_check, name="status_check"),
    path("history/", views.history, name="history"),
]
