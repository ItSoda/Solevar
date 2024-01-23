import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from twilio.rest import Client

from gym_management.models import IndividualEvent, Subscription

logger = logging.getLogger("main")


# Уведомления о истекании срока абонимента
@shared_task
def notify_users_one_day_before_expiry_subscription():
    one_day_before_expiry = timezone.now() + timezone.timedelta(days=1)

    subscriptions_to_notify = Subscription.objects.filter(
        end_date__date=one_day_before_expiry.date()
    )

    for subscription in subscriptions_to_notify:
        account_sid = settings.ACCOUNT_SID_TWILIO
        auth_token = settings.AUTH_TOKEN_TWILIO

        client = Client(account_sid, auth_token)
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
    one_trainy_before_end = 1

    individual_event_to_notify = IndividualEvent.objects.filter(
        quantity=one_trainy_before_end
    )

    for individual_event in individual_event_to_notify:
        account_sid = settings.ACCOUNT_SID_TWILIO
        auth_token = settings.AUTH_TOKEN_TWILIO

        client = Client(account_sid, auth_token)
        try:
            user = individual_event.user
            message = client.messages.create(
                from_="+19146104867",
                to=f"{user.phone_number}",
                body=f"Уважаемый {user.first_name}, ваши персональные тренировки почти закончились! Поспешите пополнить их.",
            )
        except Exception as e:
            logger.info(f"error: {str(e)}")


@shared_task
def send_email_join_success_task(added_participant, event):
    subjects = f"Запись на групповое занятие {event.title}"
    message = f"Уважаемый {added_participant.first_name}! Вы записались на групповое занятие {event.title} в {event.start_date}"
    send_mail(
        subject=subjects,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[added_participant.email],
        fail_silently=False,
    )


@shared_task
def send_email_leave_success_task(removed_participant, event):
    subjects = f"Отмена записи на групповое занятие {event.title}"
    message = f"Уважаемый {removed_participant.first_name}! Вы отменили запись на групповое занятие {event.title} в {event.start_date}"
    send_mail(
        subject=subjects,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[removed_participant.email],
        fail_silently=False,
    )
