import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class EventCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Event categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Event(models.Model):
    class Category(models.TextChoices):
        ACADEMIC = "academic", "Academic seminars"
        TECHNOLOGY = "technology", "Technology events"
        WORKSHOPS = "workshops", "Workshops"
        CAREER = "career", "Career events"
        SPORTS = "sports", "Sports"
        ENTERTAINMENT = "entertainment", "Entertainment"
        ASSOCIATION = "association", "Student association events"
        COMPETITION = "competition", "Competitions"

    class PublicationStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending", "Pending approval"
        PUBLISHED = "published", "Published"
        REJECTED = "rejected", "Rejected"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    title = models.CharField(max_length=200)
    description = models.TextField()
    external_registration_url = models.URLField(max_length=500, blank=True)
    poster = models.ImageField(upload_to="event-posters/", blank=True)
    category = models.ForeignKey(EventCategory, on_delete=models.PROTECT, related_name="events")
    legacy_category = models.CharField(max_length=30, choices=Category.choices, blank=True)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organized_events")
    venue = models.CharField(max_length=200)
    event_date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maximum_tickets = models.PositiveIntegerField()
    registration_deadline = models.DateTimeField()
    publication_status = models.CharField(max_length=20, choices=PublicationStatus.choices, default=PublicationStatus.DRAFT)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["event_date", "start_time"]
        indexes = [models.Index(fields=["publication_status", "is_approved", "event_date"])]

    @property
    def is_paid(self):
        return self.ticket_price > 0

    @property
    def poster_url(self):
        """Returns the uploaded poster URL, or a themed high-resolution photo."""
        if self.poster and hasattr(self.poster, "url"):
            try:
                return self.poster.url
            except ValueError:
                pass

        # Title-specific custom high-resolution pictures
        title_lower = self.title.lower()
        if "hackathon" in title_lower:
            return "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1000&q=80"
        if "cultural" in title_lower or "gala" in title_lower or "festival" in title_lower:
            return "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=1000&q=80"
        if "finance" in title_lower or "trading" in title_lower:
            return "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1000&q=80"
        if "rugby" in title_lower:
            return "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=1000&q=80"
        if "career" in title_lower or "job" in title_lower or "mixer" in title_lower:
            return "https://images.unsplash.com/photo-1515187029135-18ee286d815b?auto=format&fit=crop&w=1000&q=80"
        if "bootcamp" in title_lower or "web development" in title_lower or "react" in title_lower:
            return "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1000&q=80"
        if "chess" in title_lower:
            return "https://images.unsplash.com/photo-1529699211952-734e80c4d42b?auto=format&fit=crop&w=1000&q=80"
        if "climate" in title_lower or "energy" in title_lower or "renewable" in title_lower:
            return "https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?auto=format&fit=crop&w=1000&q=80"
        if "comedy" in title_lower or "acoustic" in title_lower or "music" in title_lower:
            return "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=1000&q=80"
        if "cloud" in title_lower or "devops" in title_lower or "aws" in title_lower:
            return "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1000&q=80"
        if "derby" in title_lower or "football" in title_lower or "soccer" in title_lower:
            return "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?auto=format&fit=crop&w=1000&q=80"
        if "leadership" in title_lower or "speaking" in title_lower or "ethics" in title_lower:
            return "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1000&q=80"
        if "ai" in title_lower or "artificial intelligence" in title_lower:
            return "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=1000&q=80"

        # Category-based default fallbacks
        cat_slug = getattr(self.category, "slug", "")
        category_photos = {
            "technology-events": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1000&q=80",
            "academic-seminars": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=1000&q=80",
            "workshops": "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=1000&q=80",
            "career-events": "https://images.unsplash.com/photo-1515187029135-18ee286d815b?auto=format&fit=crop&w=1000&q=80",
            "sports": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=1000&q=80",
            "entertainment": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=1000&q=80",
            "student-association-events": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1000&q=80",
            "competitions": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1000&q=80",
        }
        return category_photos.get(
            cat_slug,
            "https://images.unsplash.com/photo-1523580494863-6f3031224c94?auto=format&fit=crop&w=1000&q=80",
        )

    @property
    def tickets_sold(self):
        """Count of confirmed bookings."""
        from bookings.models import Booking
        return Booking.objects.filter(
            event=self, status=Booking.Status.CONFIRMED,
        ).aggregate(total=models.Sum("quantity"))["total"] or 0

    @property
    def tickets_remaining(self):
        """Tickets still available (pending + confirmed count against capacity)."""
        from bookings.models import Booking
        booked = Booking.objects.filter(
            event=self, status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
        ).aggregate(total=models.Sum("quantity"))["total"] or 0
        return max(0, self.maximum_tickets - booked)

    @property
    def availability_percent(self):
        """Percentage of tickets still available, 0-100."""
        if self.maximum_tickets == 0:
            return 0
        return round(self.tickets_remaining / self.maximum_tickets * 100)

    def clean(self):
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError({"end_time": "End time must be after start time."})
        if self.ticket_price < 0:
            raise ValidationError({"ticket_price": "Ticket price cannot be negative."})

    def __str__(self):
        return self.title
