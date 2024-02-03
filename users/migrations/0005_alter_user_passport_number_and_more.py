# Generated by Django 4.2 on 2024-02-03 12:12

from django.db import migrations, models
import users.services


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_alter_user_passport_number_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="passport_number",
            field=models.CharField(
                default="",
                max_length=6,
                validators=[users.services.validate_passport_number],
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="passport_series",
            field=models.CharField(
                default="",
                max_length=4,
                validators=[users.services.validate_passport_series],
            ),
        ),
    ]