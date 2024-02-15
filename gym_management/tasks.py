import logging
from datetime import datetime

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from twilio.rest import Client

from gym_management.models import IndividualEvent, Subscription
from users.models import User

from .models import Event

logger = logging.getLogger("main")


# Уведомления о истекании срока абонимента
@shared_task
def notify_users_one_day_before_expiry_subscription():
    one_day_before_expiry = timezone.now() + timezone.timedelta(days=1)

    subscriptions_to_notify = Subscription.objects.filter(
        end_date__lte=one_day_before_expiry
    )

    account_sid = settings.ACCOUNT_SID_TWILIO
    auth_token = settings.AUTH_TOKEN_TWILIO

    client = Client(account_sid, auth_token)

    for subscription in subscriptions_to_notify:
        try:
            user = subscription.user
            message = client.messages.create(
                from_="+19146104867",
                to=f"{user.phone_number}",
                body=f"Уважаемый {user.first_name}, ваш абонемент почти закончился! Остался всего день. Скорее пополните его!",
            )
        except Exception as e:
            logger.info(f"error: {str(e)}")


# Уведомления о количестве тренировок
@shared_task
def notify_users_one_trainy_before_expiry_individual_event():
    one_trainy_before_end = 2

    individual_event_to_notify = IndividualEvent.objects.filter(
        quantity=one_trainy_before_end
    )

    account_sid = settings.ACCOUNT_SID_TWILIO
    auth_token = settings.AUTH_TOKEN_TWILIO

    client = Client(account_sid, auth_token)

    for individual_event in individual_event_to_notify:
        try:
            user = individual_event.participant
            message = client.messages.create(
                from_="+19146104867",
                to=f"{user.phone_number}",
                body=f"Уважаемый {user.first_name}, ваши персональные тренировки почти закончились! Поспешите пополнить их.",
            )
        except Exception as e:
            logger.info(f"error: {str(e)}")


@shared_task
def send_email_join_success_task(email, first_name, event_id):
    event = Event.objects.get(id=event_id)
    subjects = f"Запись на групповое занятие {event.title}"
    message = (
        f"Уважаемый {first_name}! Вы записались на групповое занятие {event.title}"
    )
    send_mail(
        subject=subjects,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )


@shared_task
def send_email_leave_success_task(email, first_name, event_id):
    event = Event.objects.get(id=event_id)
    subjects = f"Отмена записи на групповое занятие {event.title}"
    message = (
        f"Уважаемый {first_name}! Вы отменили запись на групповое занятие {event.title}"
    )
    send_mail(
        subject=subjects,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )


@shared_task
def send_email_succes_buy_personal_trainer(email, first_name, coach_id, training_date):
    # Получение данных
    coach = User.objects.get(id=coach_id)
    formatted_date = datetime.strptime(training_date, "%d-%m-%Y %H:%M")

    subjects = f"Успешная оплата персональной тренировки!"
    message = f"Уважаемый {first_name}! Вы успешно оплатили и записались на персональную тренировку к {coach.full_name()} на {formatted_date.strftime('%H:%M')}"
    send_mail(
        subject=subjects,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )
