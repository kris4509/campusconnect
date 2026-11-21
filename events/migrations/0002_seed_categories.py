from django.db import migrations


def seed_categories(apps, schema_editor):
    category = apps.get_model("events", "EventCategory")
    for name, slug in [
        ("Academic seminars", "academic-seminars"),
        ("Technology events", "technology-events"),
        ("Workshops", "workshops"),
        ("Career events", "career-events"),
        ("Sports", "sports"),
        ("Entertainment", "entertainment"),
        ("Student association events", "student-association-events"),
        ("Competitions", "competitions"),
    ]:
        category.objects.get_or_create(slug=slug, defaults={"name": name})


class Migration(migrations.Migration):
    dependencies = [("events", "0001_initial")]
    operations = [migrations.RunPython(seed_categories, migrations.RunPython.noop)]
