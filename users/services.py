import logging
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils.timezone import now
from twilio.rest import Client
from datetime import timedelta

from django.utils.timezone import now
import random
import vonage

logger = logging.getLogger("main")


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


def user_change_balance(user_id, notification):
    from users.models import User

    user = User.objects.get(id=user_id)

    user.balance += notification.object.payment.amount.value
    user.save()


# PHONE VERIFICATION
def send_verification_phone(phone_number, code):
    api_key = "2294fcd4"
    api_secret = "IZ4FDUUrycolekVI"

    client = vonage.Client(key=api_key, secret=api_secret)
    sms = vonage.Sms(client)
    try:
        message = sms.send_message(
            {
                "from": "+79136757877",
                "to": f"{phone_number}",
                "text": f"{code}"
            }
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
    phone_numbers = PhoneNumberVerifySMS.objects.filter(
        code=code, user=user
    )
    try:
        if (
            phone_numbers.exists()
            and not phone_numbers.last().is_expired()
        ):
            return True
        return False
    except Exception as e:
        return False
    

def send_phone_verify_task(phone_number):
    from users.models import PhoneNumberVerifySMS, User
    expiration = now() + timedelta(hours=24)
    code = str(random.randint(1000, 9999))
    record = PhoneNumberVerifySMS.objects.create(
        code=code, phone_number=phone_number, expiration=expiration
    )
    record.send_verification_phone()
