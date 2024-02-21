import uuid
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now

from users.models import EmailVerifications, User


@shared_task
def send_email_success_register(name, email):
    subjects = f"Успешная регистрация в фитнес-клубе ПАПА ФИТНЕСС"
    message = (
        f"Уважаемый {name}! Поздравляем с успешной регистрацией в сервисе ПАПА ФИТНЕСС"
    )
    send_mail(
        subject=subjects,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )


@shared_task
def send_email_verify_task(user_id):
    user = User.objects.get(id=user_id)
    expiration = now() + timedelta(hours=24)
    record = EmailVerifications.objects.create(
        code=uuid.uuid4(), user=user, expiration=expiration
    )
    record.send_verification_email()
