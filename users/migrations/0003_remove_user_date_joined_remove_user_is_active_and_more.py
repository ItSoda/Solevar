# Generated by Django 4.2 on 2024-01-18 08:05

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_user_rating"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="date_joined",
        ),
        migrations.RemoveField(
            model_name="user",
            name="is_active",
        ),
        migrations.RemoveField(
            model_name="user",
            name="is_staff",
        ),
    ]
