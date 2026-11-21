from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from bookings.models import Booking
from events.models import Event, EventCategory
from payments.models import Payment


def home(request):
    featured = Event.objects.filter(publication_status=Event.PublicationStatus.PUBLISHED, is_approved=True).select_related("category").order_by("event_date", "start_time")[:12]
    categories = EventCategory.objects.all()
    return render(request, "dashboard/home.html", {"featured": featured, "categories": categories})


@login_required
def student_dashboard(request):
    bookings = Booking.objects.filter(student=request.user).select_related("event").order_by("-created_at")[:5]
    return render(request, "dashboard/student.html", {"bookings": bookings})


def role_required(role):
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            if request.user.role != role and not request.user.is_superuser:
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


@role_required("organizer")
def organizer_dashboard(request):
    events = Event.objects.filter(organizer=request.user).order_by("-created_at")
    return render(request, "dashboard/organizer.html", {"events": events})


@role_required("admin")
def admin_dashboard(request):
    context = {
        "pending_events": Event.objects.filter(publication_status=Event.PublicationStatus.PENDING, is_approved=False).count(),
        "published_events": Event.objects.filter(publication_status=Event.PublicationStatus.PUBLISHED).count(),
        "users": get_user_model().objects.count(),
        "bookings": Booking.objects.count(),
        "payments": Payment.objects.count(),
    }
    return render(request, "dashboard/admin.html", context)


@role_required("admin")
def event_approvals(request):
    events = Event.objects.filter(publication_status=Event.PublicationStatus.PENDING).select_related("organizer", "category")
    return render(request, "dashboard/event_approvals.html", {"events": events})


@role_required("admin")
def event_approval_action(request, pk, action):
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        if action == "approve":
            event.is_approved = True
            event.publication_status = Event.PublicationStatus.PUBLISHED
            messages.success(request, "Event approved and published.")
        elif action == "reject":
            event.is_approved = False
            event.publication_status = Event.PublicationStatus.REJECTED
            messages.success(request, "Event rejected.")
        event.save(update_fields=["is_approved", "publication_status", "updated_at"])
    return redirect("dashboard:event_approvals")


@role_required("admin")
def user_management(request):
    users = get_user_model().objects.all().order_by("-created_at")
    return render(request, "dashboard/users.html", {"users": users})


@role_required("admin")
def booking_management(request):
    bookings = Booking.objects.select_related("event", "student").prefetch_related("payments", "ticket").order_by("-created_at")
    return render(request, "dashboard/bookings.html", {"bookings": bookings})


@role_required("admin")
def payment_management(request):
    payments = Payment.objects.select_related("booking", "booking__event", "booking__student").order_by("-created_at")
    return render(request, "dashboard/payments.html", {"payments": payments})


def about(request):
    return render(request, "dashboard/about.html")


def contact(request):
    return render(request, "dashboard/contact.html")
