# Generated by Django 4.2 on 2024-02-05 15:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("gym_management", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subscription",
            name="price",
            field=models.BigIntegerField(default=1000),
        ),
        migrations.DeleteModel(
            name="Club",
        ),
    ]
