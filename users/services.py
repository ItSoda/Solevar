import logging
import random
from datetime import timedelta

from django.core.mail import EmailMessage
from django.urls import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from twilio.rest import Client
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger("main")


def send_email_from_user(subject, message, phone_number, email, photo_path=None):
    email = EmailMessage(
        subject=subject,
        body=f"Клиент - email: {email} | phone_number: {phone_number}. \n\n{message}",
        from_email=settings.EMAIL_HOST_USER,
        to=[settings.EMAIL_HOST_USER],
    )

    if photo_path:
        with open(photo_path, 'rb') as photo_file:
            email.attach_file(photo_path, mimetype='image/jpeg')

    email.send(fail_silently=False)
    


# YOOKASSA PAYMENT
def create_payment(email, amount, user, request):
    from django.conf import settings
    from yookassa import Configuration, Payment

    # Ключи доступа
    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    # Объект платежа
    payment = Payment.create(
        {
            "amount": {"value": str(amount), "currency": "RUB"},
            "payment_method_data": {"type": "bank_card"},
            "confirmation": {
                "type": "redirect",
                "return_url": settings.YOOKASSA_REDIRECT_URL,
            },
            "capture": True,
            "description": f"Платеж для пользователя {email}",
            "metadata": {"userId": str(user.id)},
        }
    )
    return payment.confirmation.confirmation_url


def user_change_balance(user_id, value):
    try:
        from users.models import User
        user = User.objects.get(id=user_id)
        user.balance += int(value)
        user.save()
    except Exception as e:
        logging.info(f"error: {str(e)}")


# PHONE VERIFICATION
def send_verification_phone(phone_number, code):
    account_sid = settings.ACCOUNT_SID_TWILIO
    auth_token = settings.AUTH_TOKEN_TWILIO

    client = Client(account_sid, auth_token)
    try:
        message = client.messages.create(
            from_="+19146104867", to=f"{phone_number}", body=f"code - {code}"
        )
    except Exception as e:
        logger.info(f"error: {str(e)}")


def is_expired(self):
    if now() >= self.expiration:
        self.delete()
        self.save()
        return True
    return False


def proccess_phone_verification(code, phone_number):
    from users.models import PhoneNumberVerifySMS, User

    user = get_object_or_404(User, phone_number=phone_number)
    phone_numbers = PhoneNumberVerifySMS.objects.filter(code=code, user=user)
    try:
        if phone_numbers.exists() and not phone_numbers.last().is_expired():
            return True
        return False
    except Exception as e:
        return False


def send_phone_verify_task(phone_number):
    from users.models import PhoneNumberVerifySMS

    expiration = now() + timedelta(hours=24)
    code = str(random.randint(1000, 9999))
    record = PhoneNumberVerifySMS.objects.create(
        code=code, phone_number=phone_number, expiration=expiration
    )
    record.send_verification_phone()
