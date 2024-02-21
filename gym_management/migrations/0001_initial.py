# Generated by Django 4.2 on 2024-02-21 07:18

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Event",
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
                ("title", models.CharField(max_length=128)),
                ("content", models.TextField()),
                ("limit_of_participants", models.SmallIntegerField()),
                ("start_date", models.DateTimeField()),
                ("duration", models.PositiveIntegerField(default=0)),
                ("club", models.CharField(default="Рекорд фитнес ЭКО", max_length=150)),
                ("price", models.PositiveBigIntegerField(default=0)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("waiting", "Waiting"),
                            ("canceled", "Canceled"),
                            ("passed", "Passed"),
                            ("edit", "Edit"),
                        ],
                        default="waiting",
                        max_length=20,
                    ),
                ),
            ],
            options={
                "verbose_name": "тренировку",
                "verbose_name_plural": "Тренировки",
            },
        ),
        migrations.CreateModel(
            name="IndividualEvent",
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
                ("training_date", models.DateTimeField(unique=True)),
                ("description", models.TextField(default="Personal training")),
                ("duration", models.PositiveIntegerField(default=60)),
                ("quantity", models.IntegerField(default=1)),
                ("price", models.PositiveBigIntegerField(default=0)),
            ],
            options={
                "verbose_name": "персональную тренировку",
                "verbose_name_plural": "Персональные тренировки",
            },
        ),
        migrations.CreateModel(
            name="Subscription",
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
                ("number", models.BigIntegerField(unique=True)),
                ("start_date", models.DateTimeField(auto_now_add=True)),
                ("duration", models.IntegerField()),
                ("price", models.BigIntegerField(default=1000)),
                ("end_date", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "aбонемент",
                "verbose_name_plural": "абонементы",
            },
        ),
        migrations.CreateModel(
            name="Tag",
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
                ("name", models.CharField(max_length=64)),
            ],
            options={
                "verbose_name": "тег",
                "verbose_name_plural": "Теги",
            },
        ),
    ]
