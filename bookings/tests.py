from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from bookings.models import Booking
from bookings.services import BookingError, create_booking
from events.models import Event, EventCategory


class BookingTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="student", email="student@example.edu", password="StrongPass!923",
            full_name="Student", phone_number="254712345678",
        )
        self.organizer = User.objects.create_user(
            username="organizer", email="organizer@example.edu", password="StrongPass!923",
            full_name="Organizer", phone_number="254712345679", role="organizer",
        )
        category = EventCategory.objects.create(name="Workshops Test", slug="workshops-test")
        self.event = Event.objects.create(
            title="Test Workshop",
            description="A test event",
            category=category,
            organizer=self.organizer,
            venue="Main Hall",
            event_date=timezone.localdate() + timedelta(days=7),
            start_time="10:00",
            end_time="12:00",
            ticket_price=0,
            maximum_tickets=2,
            registration_deadline=timezone.now() + timedelta(days=5),
            publication_status=Event.PublicationStatus.PUBLISHED,
            is_approved=True,
        )

    def test_free_booking_is_confirmed_and_creates_ticket(self):
        booking = create_booking(self.student, self.event.pk)
        self.assertEqual(booking.status, Booking.Status.CONFIRMED)
        self.assertTrue(hasattr(booking, "ticket"))

    def test_duplicate_booking_is_rejected(self):
        create_booking(self.student, self.event.pk)
        with self.assertRaises(BookingError):
            create_booking(self.student, self.event.pk)
