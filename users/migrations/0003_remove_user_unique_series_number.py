# Generated by Django 4.2 on 2024-02-03 10:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_alter_user_date_of_birth"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="user",
            name="unique_series_number",
        ),
    ]