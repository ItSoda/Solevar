from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import CustomUserManager
from phonenumber_field.modelfields import PhoneNumberField

# User Model
class User(AbstractUser):
    """Model for Users"""

    COACH = "coach"
    CLIENT = "client"

    ROLES_CHOICES = (
        (COACH, "Coach"),
        (CLIENT, "Client"),
    )

    phone_number = PhoneNumberField(unique=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50, default="first name")
    last_name = models.CharField(max_length=50, default="last name")
    is_verified_email = models.BooleanField(default=False)
    description = models.TextField(default="about you")
    photo = models.ImageField(
        upload_to="user_images", default="user_images/no-profile.png"
    )
    yookassa_payment_id = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLES_CHOICES, default=CLIENT)
    rating = models.SmallIntegerField(default=5)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["email", "username"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "пользователя"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"Пользователь {self.email} | {self.first_name}"
