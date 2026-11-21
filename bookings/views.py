import base64
import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from bookings.models import Booking, Ticket
from bookings.services import BookingError, create_booking
from events.models import Event


def _generate_qr_base64(data):
    """Return a base64-encoded PNG QR code for *data*, or None if the
    qrcode library is not installed."""
    try:
        import qrcode
    except ImportError:
        return None
    qr = qrcode.QRCode(version=1, box_size=10, border=3)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f172a", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


@login_required
def booking_list(request):
    bookings = Booking.objects.filter(student=request.user).select_related("event").prefetch_related("payments", "ticket")
    return render(request, "bookings/list.html", {"bookings": bookings})


@login_required
def create(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    try:
        booking = create_booking(request.user, event_id)
    except BookingError as exc:
        messages.error(request, str(exc))
        return redirect("events:detail", pk=event_id)
    except Event.DoesNotExist:
        messages.error(request, "This event could not be found.")
        return redirect("events:list")

    if event.is_paid:
        messages.info(request, "Complete payment to confirm this booking.")
        return redirect("payments:pay", booking_id=booking.id)
    messages.success(request, "Your free ticket is confirmed.")
    return redirect("bookings:tickets")


@login_required
def cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, student=request.user)
    if request.method == "POST" and booking.status != Booking.Status.CANCELLED:
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status", "updated_at"])
        if hasattr(booking, "ticket"):
            booking.ticket.status = Ticket.Status.CANCELLED
            booking.ticket.save(update_fields=["status"])
        messages.success(request, "Booking cancelled.")
    return redirect("bookings:list")


@login_required
def tickets(request):
    tickets = Ticket.objects.filter(booking__student=request.user).select_related("booking__event")
    return render(request, "bookings/tickets.html", {"tickets": tickets})


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, booking__student=request.user)
    qr_data = f"CAMPUSCONNECT:TICKET:{ticket.reference}:EVENT:{ticket.booking.event_id}"
    qr_base64 = _generate_qr_base64(qr_data)
    return render(request, "bookings/ticket_detail.html", {
        "ticket": ticket,
        "qr_code": qr_base64,
    })
