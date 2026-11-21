from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EventForm
from .models import Event, EventCategory


def event_list(request):
    events = Event.objects.filter(publication_status=Event.PublicationStatus.PUBLISHED, is_approved=True)
    query = request.GET.get("q")
    category = request.GET.get("category")
    date = request.GET.get("date")
    price = request.GET.get("price")
    if query:
        events = events.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category:
        events = events.filter(category_id=category)
    if date:
        events = events.filter(event_date=date)
    if price == "free":
        events = events.filter(ticket_price=0)
    elif price == "paid":
        events = events.filter(ticket_price__gt=0)
    return render(request, "events/list.html", {
        "events": events,
        "query": query,
        "category": category,
        "date": date,
        "price": price,
        "categories": EventCategory.objects.all(),
    })


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, publication_status=Event.PublicationStatus.PUBLISHED, is_approved=True)
    return render(request, "events/detail.html", {"event": event})


def organizer_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "organizer":
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return login_required(wrapper)


@organizer_required
def event_create(request):
    form = EventForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        event = form.save(commit=False)
        event.organizer = request.user
        event.publication_status = Event.PublicationStatus.PENDING
        event.save()
        messages.success(request, "Event submitted for administrator approval.")
        return redirect("dashboard:organizer")
    return render(request, "events/form.html", {"form": form, "action": "Create event"})


@organizer_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk, organizer=request.user)
    form = EventForm(request.POST or None, request.FILES or None, instance=event)
    if request.method == "POST" and form.is_valid():
        changed = form.save(commit=False)
        if changed.publication_status not in (Event.PublicationStatus.REJECTED, Event.PublicationStatus.CANCELLED):
            changed.publication_status = Event.PublicationStatus.PENDING
            changed.is_approved = False
        changed.save()
        messages.success(request, "Event changes saved.")
        return redirect("dashboard:organizer")
    return render(request, "events/form.html", {"form": form, "action": "Edit event", "event": event})


@organizer_required
def event_attendees(request, pk):
    event = get_object_or_404(Event, pk=pk, organizer=request.user)
    bookings = event.bookings.select_related("student", "ticket").prefetch_related("payments").order_by("-created_at")
    return render(request, "events/attendees.html", {"event": event, "bookings": bookings})
