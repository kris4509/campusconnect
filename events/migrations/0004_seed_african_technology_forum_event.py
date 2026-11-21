from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.db import migrations
from django.utils import timezone


def seed_event(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    EventCategory = apps.get_model("events", "EventCategory")
    Event = apps.get_model("events", "Event")

    organizer, created = User.objects.get_or_create(
        email="mutua@africantechnologyforum.org",
        defaults={
            "username": "mutua@africantechnologyforum.org",
            "full_name": "African Technology Forum",
            "phone_number": "254734466233",
            "role": "organizer",
            "is_approved": True,
        },
    )
    if created:
        organizer.password = make_password(None)
        organizer.save(update_fields=["password"])

    category = EventCategory.objects.get(slug="technology-events")
    Event.objects.update_or_create(
        title="Building with AI",
        defaults={
            "description": (
                "The African Technology Forum is coming to Egerton for a hands-on Building with AI "
                "session. Meet other builders, form a team and get ready for the ATF AI Challenge.\n\n"
                "Agenda:\n"
                "1. The ATF AI Challenge: how it works and how to win.\n"
                "2. AI School: hear from students who have finished it.\n"
                "3. Team formation: find a team of 3 to 5 and choose a problem.\n"
                "4. Next steps: proposals, mentors and key dates.\n\n"
                "Free to attend. Seats are limited; please bring your laptop."
            ),
            "external_registration_url": "",
            "category": category,
            "organizer": organizer,
            "venue": "CoELIB, Egerton University",
            "event_date": datetime(2026, 11, 25).date(),
            "start_time": datetime.strptime("09:00", "%H:%M").time(),
            "end_time": datetime.strptime("13:00", "%H:%M").time(),
            "ticket_price": 300,
            "maximum_tickets": 100,
            "registration_deadline": timezone.make_aware(datetime(2026, 11, 25, 6, 0)),
            "publication_status": "published",
            "is_approved": True,
        },
    )


def remove_event(apps, schema_editor):
    Event = apps.get_model("events", "Event")
    Event.objects.filter(title="Building with AI").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0003_event_external_registration_url"),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_event, remove_event),
    ]
