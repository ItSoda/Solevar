# Generated by Django 4.2 on 2024-01-27 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym_management', '0005_rename_start_date_individualevent_training_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='individualevent',
            name='training_date',
            field=models.DateTimeField(unique=True),
        ),
    ]
