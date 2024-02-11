# Generated by Django 4.2 on 2024-02-11 04:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0009_alter_user_photo"),
    ]

    operations = [
        migrations.CreateModel(
            name="AudioRecord",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("record_file", models.FileField(upload_to="")),
            ],
        ),
        migrations.AddField(
            model_name="user",
            name="records_files",
            field=models.ManyToManyField(blank=True, null=True, to="users.audiorecord"),
        ),
    ]