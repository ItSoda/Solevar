# Generated by Django 4.2 on 2024-02-13 09:46

import django.utils.timezone
import phonenumber_field.modelfields
from django.conf import settings
from django.db import migrations, models

import users.services


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        max_length=128, region=None, unique=True
                    ),
                ),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("first_name", models.CharField(default="Имя", max_length=50)),
                ("last_name", models.CharField(default="Фамилия", max_length=50)),
                ("patronymic", models.CharField(default="Отчество", max_length=50)),
                ("is_verified_email", models.BooleanField(default=False)),
                ("description", models.TextField(default="Мое описание")),
                ("photo", models.ImageField(blank=True, null=True, upload_to="")),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("coach", "Coach"),
                            ("client", "Client"),
                            ("admin", "Admin"),
                        ],
                        default="client",
                        max_length=20,
                    ),
                ),
                ("rating", models.SmallIntegerField(default=5)),
                (
                    "trainer_type",
                    models.CharField(default="Пользователь", max_length=100),
                ),
                ("balance", models.BigIntegerField(default=0)),
                (
                    "passport_series",
                    models.CharField(
                        default="",
                        max_length=4,
                        validators=[users.services.validate_passport_series],
                    ),
                ),
                (
                    "passport_number",
                    models.CharField(
                        default="",
                        max_length=6,
                        validators=[users.services.validate_passport_number],
                    ),
                ),
                ("date_of_issue", models.DateField(blank=True, null=True)),
                ("place_of_issue", models.CharField(max_length=70)),
                ("registration_address", models.CharField(max_length=120)),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
            ],
            options={
                "verbose_name": "пользователя",
                "verbose_name_plural": "Клиенты | Тренеры",
            },
        ),
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
                ("name", models.CharField(max_length=120)),
                ("record_file", models.FileField(max_length=500, upload_to="")),
            ],
            options={
                "verbose_name": "запись звонка",
                "verbose_name_plural": "Записи звонков",
            },
        ),
        migrations.CreateModel(
            name="PhoneNumberVerifySMS",
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
                ("code", models.CharField(max_length=4, unique=True)),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        max_length=128, region=None
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("expiration", models.DateTimeField()),
            ],
            options={
                "verbose_name": "код подтверждения",
                "verbose_name_plural": "Коды подтверждения",
            },
        ),
        migrations.CreateModel(
            name="Schedule",
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
                ("time", models.DateTimeField()),
                ("is_selected", models.BooleanField(default=False)),
                ("coach", models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "время занятия",
                "verbose_name_plural": "Расписание занятий",
            },
        ),
        migrations.AddField(
            model_name="user",
            name="records_files",
            field=models.ManyToManyField(blank=True, null=True, to="users.audiorecord"),
        ),
        migrations.AddField(
            model_name="user",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.permission",
                verbose_name="user permissions",
            ),
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(
                fields=(
                    "passport_series",
                    "passport_number",
                    "place_of_issue",
                    "registration_address",
                    "date_of_issue",
                ),
                name="unique_passport",
            ),
        ),
    ]
