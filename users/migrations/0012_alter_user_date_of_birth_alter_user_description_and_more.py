# Generated by Django 4.2 on 2024-02-11 05:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0011_alter_audiorecord_options_audiorecord_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="date_of_birth",
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="records_files",
            field=models.ManyToManyField(blank=True, to="users.audiorecord"),
        ),
        migrations.AlterField(
            model_name="user",
            name="trainer_type",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
