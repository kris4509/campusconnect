import uuid

from django.conf import settings
from django.db import models

from events.models import Event


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="bookings")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    reference = models.CharField(max_length=20, unique=True, editable=False)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["event", "student"], condition=models.Q(status__in=["pending", "confirmed"]), name="unique_active_event_booking"),
        ]
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"CC-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} - {self.event.title}"


class Ticket(models.Model):
    class Status(models.TextChoices):
        VALID = "valid", "Valid"
        USED = "used", "Used"
        CANCELLED = "cancelled", "Cancelled"

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="ticket")
    reference = models.CharField(max_length=24, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.VALID)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"TKT-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
