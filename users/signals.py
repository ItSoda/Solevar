from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import User
from .tasks import send_email_success_register


@receiver(post_save, sender=User)
def success_register_user(sender, instance, created, **kwargs):
    if created:
        send_email_success_register.delay(instance.first_name, instance.email)