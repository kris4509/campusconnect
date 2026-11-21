from django.db import migrations


def configure_booking(apps, schema_editor):
    Event = apps.get_model("events", "Event")
    Event.objects.filter(title="Building with AI").update(
        ticket_price=300,
        external_registration_url="",
    )


def reverse_booking(apps, schema_editor):
    Event = apps.get_model("events", "Event")
    Event.objects.filter(title="Building with AI").update(
        ticket_price=0,
        external_registration_url="https://forms.gle/sdvrnFmpxQW5bDYe9",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0004_seed_african_technology_forum_event"),
    ]

    operations = [
        migrations.RunPython(configure_booking, reverse_booking),
    ]
