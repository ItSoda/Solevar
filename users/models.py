from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from users.services import is_expired, send_verification_email

from .managers import CustomUserManager
from .services import (is_expired, send_verification_phone,
                       upload_audio_to_yandex_cloud,
                       upload_media_to_yandex_cloud, validate_passport_number,
                       validate_passport_series)


class AudioRecord(models.Model):
    name = models.CharField(max_length=120)
    record_file = models.FileField(max_length=500)

    class Meta:
        verbose_name = "запись звонка"
        verbose_name_plural = "Записи звонков"

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        upload_audio_to_yandex_cloud(self)
        super().save(args, **kwargs)


# User Model
class User(AbstractUser):
    """Model for Users"""

    COACH = "coach"
    CLIENT = "client"
    ADMIN = "admin"

    ROLES_CHOICES = (
        (COACH, "Coach"),
        (CLIENT, "Client"),
        (ADMIN, "Admin"),
    )

    phone_number = PhoneNumberField(unique=True)
    email = models.EmailField(blank=True)
    first_name = models.CharField(max_length=50, default="Имя")
    last_name = models.CharField(max_length=50, default="Фамилия")
    patronymic = models.CharField(max_length=50, default="Отчество")
    is_verified_email = models.BooleanField(default=False)
    description = models.TextField(default="Мое описание")
    photo_file = models.ImageField(blank=True, null=True)
    photo = models.CharField(
        max_length=500,
        default="https://storage.yandexcloud.net/solevar-bucket/user_images/no-profile.png",
        null=True,
        blank=True,
    )
    role = models.CharField(max_length=20, choices=ROLES_CHOICES, default=CLIENT)
    rating = models.SmallIntegerField(default=5)
    trainer_type = models.CharField(max_length=100, default="Пользователь")
    balance = models.BigIntegerField(default=0)
    passport_series = models.CharField(
        max_length=4, validators=[validate_passport_series], default=""
    )
    passport_number = models.CharField(
        max_length=6, validators=[validate_passport_number], default=""
    )
    date_of_issue = models.DateField(blank=True, null=True)
    place_of_issue = models.CharField(max_length=70)
    registration_address = models.CharField(max_length=120)
    date_of_birth = models.DateField(blank=True, null=True)
    records_files = models.ManyToManyField(AudioRecord, blank=True, null=True)

    username = None

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = "пользователя"
        verbose_name_plural = "Клиенты | Тренеры"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "passport_series",
                    "passport_number",
                    "place_of_issue",
                    "registration_address",
                    "date_of_issue",
                ],
                name="unique_passport",
            )
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.patronymic}"

    def save(self, *args, **kwargs):
        upload_media_to_yandex_cloud(self)
        super().save(args, **kwargs)

    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}"

    # def event_history(self):
    #     from gym_management.serializers import EventSerializer
    #     Event = apps.get_model("gym_management", "Event")
    #     return EventSerializer(Event.objects.filter(participants=self, status="Passed"), many=True).data


class PhoneNumberVerifySMS(models.Model):
    code = models.CharField(unique=True, max_length=4)
    phone_number = PhoneNumberField()
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    class Meta:
        verbose_name = "код подтверждения"
        verbose_name_plural = "Коды подтверждения"

    def __str__(self):
        return f"PhoneNumberVerifySMS object for {self.phone_number}"

    def send_verification_phone(self):
        send_verification_phone(self.phone_number, self.code)

    def is_expired(self):
        is_expired(self)


class Schedule(models.Model):
    time = models.DateTimeField()
    is_selected = models.BooleanField(default=False)
    coach = models.ManyToManyField(User)

    class Meta:
        verbose_name = "время занятия"
        verbose_name_plural = "Расписание занятий"

    def __str__(self):
        return f"Time: {self.time}"


class EmailVerifications(models.Model):
    """Model for one EmailVerifications"""

    code = models.UUIDField(unique=True, null=True, blank=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"EmailVerification object for {self.user.email}"

    def send_verification_email(self):
        send_verification_email(self.user.email, self.code)

    def is_expired(self):
        is_expired(self)
