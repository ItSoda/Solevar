# Generated by Django 4.2 on 2024-02-08 20:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("chats", "0004_alter_room_agent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="room",
            name="agent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="rooms",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
