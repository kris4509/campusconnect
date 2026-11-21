from django.db import models, transaction
from django.utils import timezone

from bookings.models import Booking, Ticket
from events.models import Event


class BookingError(Exception):
    pass


@transaction.atomic
def create_booking(student, event_id):
    event = Event.objects.select_for_update().select_related("organizer").get(pk=event_id)
    if event.publication_status != Event.PublicationStatus.PUBLISHED or not event.is_approved:
        raise BookingError("This event is not available for booking.")
    if event.registration_deadline <= timezone.now():
        raise BookingError("The registration deadline has passed.")
    if Booking.objects.filter(event=event, student=student, status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED]).exists():
        raise BookingError("You already have an active booking for this event.")
    booked = Booking.objects.filter(event=event, status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED]).aggregate(total=models.Sum("quantity"))["total"] or 0
    if booked >= event.maximum_tickets:
        raise BookingError("There are no tickets remaining.")

    status = Booking.Status.PENDING
    booking = Booking.objects.create(event=event, student=student, quantity=1, status=status)
    if not event.is_paid:
        booking.status = Booking.Status.CONFIRMED
        booking.save(update_fields=["status", "updated_at"])
        Ticket.objects.create(booking=booking)
    return booking


@transaction.atomic
def confirm_paid_booking(booking):
    booking = Booking.objects.select_for_update().select_related("event").get(pk=booking.pk)
    if booking.status == Booking.Status.CONFIRMED:
        return booking
    booked = Booking.objects.filter(event=booking.event, status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED]).exclude(pk=booking.pk).aggregate(total=models.Sum("quantity"))["total"] or 0
    if booked >= booking.event.maximum_tickets:
        booking.status = Booking.Status.EXPIRED
        booking.save(update_fields=["status", "updated_at"])
        raise BookingError("The event sold out before payment could be confirmed.")
    booking.status = Booking.Status.CONFIRMED
    booking.save(update_fields=["status", "updated_at"])
    Ticket.objects.get_or_create(booking=booking)
    return booking
