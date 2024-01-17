from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from phonenumber_field.phonenumber import to_python


class CustomUserManager(BaseUserManager):
    def create_user(self, username, phone_number, password=None, email=None,  **extra_fields):
        if not email and not phone_number:
            raise ValueError(("The email or phone number must be set"))

        email = self.normalize_email(email)
        phone_number = to_python(phone_number)

        user = self.model(username=username, phone_number=str(phone_number), email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, phone_number, password, email=None,  **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(username, email, password, phone_number, **extra_fields)