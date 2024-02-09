from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from .managers import CustomUserManager
from .services import (is_expired, send_verification_phone,
                       validate_passport_number, validate_passport_series)
from django.apps import apps
from .services import upload_to_yandex_cloud

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
    description = models.TextField(default="about you")
    photo = models.ImageField(
        upload_to="user_images", default="media/user_images/no-profile.png"
    )
    role = models.CharField(max_length=20, choices=ROLES_CHOICES, default=CLIENT)
    rating = models.SmallIntegerField(default=5)
    trainer_type = models.CharField(max_length=100, default="")
    balance = models.BigIntegerField(default=0)
    passport_series = models.CharField(
        max_length=4, validators=[validate_passport_series], default=""
    )
    passport_number = models.CharField(
        max_length=6, validators=[validate_passport_number], default=""
    )
    date_of_birth = models.DateField(default="2024-02-02")
    username = None

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = "пользователя"
        verbose_name_plural = "Клиенты | Тренеры"
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=["passport_series", "passport_number"],
        #         name="unique_series_number",
        #     )
        # ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.patronymic}"
    
    def save(self, *args, **kwargs):
        upload_to_yandex_cloud(self)
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
