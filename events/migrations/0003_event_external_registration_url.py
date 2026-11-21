from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0002_seed_categories"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="external_registration_url",
            field=models.URLField(blank=True, max_length=500),
        ),
    ]
