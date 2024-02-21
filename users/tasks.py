from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_email_success_register(name, email):
    subjects = f"Успешная регистрация в фитнес-клубе ПАПА ФИТНЕСС"
    message = f"Уважаемый {name}! Поздравляем с успешной регистрацией в сервисе ПАПА ФИТНЕСС"
    send_mail(
        subject=subjects,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )