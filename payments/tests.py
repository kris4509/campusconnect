import json
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from bookings.models import Booking
from events.models import Event, EventCategory
from payments.models import Payment


class PaymentCallbackTests(TestCase):
    def setUp(self):
        student = User.objects.create_user(
            username="student", email="student@example.edu", password="StrongPass!923",
            full_name="Student", phone_number="254712345678",
        )
        organizer = User.objects.create_user(
            username="organizer", email="organizer@example.edu", password="StrongPass!923",
            full_name="Organizer", phone_number="254712345679", role="organizer",
        )
        category = EventCategory.objects.create(name="Paid Test", slug="paid-test")
        event = Event.objects.create(
            title="Paid Event",
            description="Paid test event",
            category=category,
            organizer=organizer,
            venue="Hall",
            event_date=timezone.localdate() + timedelta(days=7),
            start_time="10:00",
            end_time="12:00",
            ticket_price=500,
            maximum_tickets=10,
            registration_deadline=timezone.now() + timedelta(days=5),
            publication_status=Event.PublicationStatus.PUBLISHED,
            is_approved=True,
        )
        self.booking = Booking.objects.create(
            event=event, student=student, status=Booking.Status.PENDING,
        )
        self.payment = Payment.objects.create(
            booking=self.booking,
            provider=Payment.Provider.DARJA,
            amount=500,
            phone_number="254712345678",
            checkout_request_id="checkout-123",
        )

    def callback_payload(self, result_code=0):
        result = {
            "CheckoutRequestID": "checkout-123",
            "ResultCode": result_code,
            "ResultDesc": "Payment successful" if result_code == 0 else "Payment failed",
        }
        if result_code == 0:
            result["CallbackMetadata"] = {"Item": [{"Name": "MpesaReceiptNumber", "Value": "QA123456"}]}
        return {"Body": {"stkCallback": result}}

    def test_success_callback_confirms_booking_and_creates_ticket(self):
        response = self.client.post(
            reverse("payments:callback"),
            data=json.dumps(self.callback_payload()),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.payment.refresh_from_db()
        self.assertEqual(self.booking.status, Booking.Status.CONFIRMED)
        self.assertTrue(hasattr(self.booking, "ticket"))
        self.assertEqual(self.payment.status, Payment.Status.SUCCESSFUL)

    def test_duplicate_success_callback_is_idempotent(self):
        payload = json.dumps(self.callback_payload())
        self.client.post(reverse("payments:callback"), data=payload, content_type="application/json")
        response = self.client.post(reverse("payments:callback"), data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Payment.objects.filter(checkout_request_id="checkout-123").count(), 1)
