# Generated by Django 4.2 on 2024-02-11 04:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("gym_management", "0011_alter_event_participants"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="tags",
            field=models.ManyToManyField(
                blank=True, default="", to="gym_management.tag"
            ),
        ),
    ]