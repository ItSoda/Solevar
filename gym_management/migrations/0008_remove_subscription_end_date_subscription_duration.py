# Generated by Django 4.2 on 2024-01-21 12:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("gym_management", "0007_alter_subscription_number"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="subscription",
            name="end_date",
        ),
        migrations.AddField(
            model_name="subscription",
            name="duration",
            field=models.IntegerField(default=30),
        ),
    ]