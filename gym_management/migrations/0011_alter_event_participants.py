# Generated by Django 4.2 on 2024-02-07 11:53

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("gym_management", "0010_alter_event_tags"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="participants",
            field=models.ManyToManyField(
                blank=True,
                related_name="participants_event",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]