# Generated by Django 4.2 on 2024-01-26 11:57

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("gym_management", "0004_event_status"),
    ]

    operations = [
        migrations.RenameField(
            model_name="individualevent",
            old_name="start_date",
            new_name="training_date",
        ),
    ]