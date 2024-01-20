from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from .managers import CustomUserManager
from .services import is_expired, send_verification_phone


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
    email = models.EmailField(blank=True)
    first_name = models.CharField(max_length=50, default="first name")
    last_name = models.CharField(max_length=50, default="last name")
    is_verified_email = models.BooleanField(default=False)
    description = models.TextField(default="about you")
    photo = models.ImageField(
        upload_to="user_images", default="user_images/no-profile.png"
    )
    role = models.CharField(max_length=20, choices=ROLES_CHOICES, default=CLIENT)
    rating = models.SmallIntegerField(default=5)
    trainer_type = models.CharField(max_length=100, default="")
    balance = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    username = None

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = "пользователя"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"Пользователь {self.phone_number} | {self.first_name}"


class PhoneNumberVerifySMS(models.Model):
    code = models.CharField(unique=True, max_length=4)
    phone_number = PhoneNumberField()
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    def __str__(self):
        return f"PhoneNumberVerifySMS object for {self.phone_number}"

    def send_verification_phone(self):
        send_verification_phone(self.phone_number, self.code)

    def is_expired(self):
        is_expired(self)
