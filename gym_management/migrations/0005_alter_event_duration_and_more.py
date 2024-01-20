# Generated by Django 4.2 on 2024-01-20 15:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("gym_management", "0004_alter_event_duration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="duration",
            field=models.DurationField(),
        ),
        migrations.AlterField(
            model_name="individualevent",
            name="duration_minutes",
            field=models.PositiveIntegerField(default=60),
        ),
    ]