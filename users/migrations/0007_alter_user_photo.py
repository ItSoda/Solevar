# Generated by Django 4.2 on 2024-02-09 18:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_alter_user_photo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="photo",
            field=models.ImageField(
                default="media/user_images/no-profile.png", upload_to="user_images"
            ),
        ),
    ]