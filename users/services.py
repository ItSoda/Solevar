import datetime
import logging
import random
from datetime import timedelta
from decimal import Decimal

import boto3
from django.conf import settings
from django.core.mail import EmailMessage
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response
from twilio.rest import Client

logger = logging.getLogger("main")


def send_email_from_user(subject, message, phone_number, email, photo_path=None):
    email = EmailMessage(
        subject=subject,
        body=f"Клиент - email: {email} | phone_number: {phone_number}. \n\n{message}",
        from_email=settings.EMAIL_HOST_USER,
        to=[settings.EMAIL_HOST_USER],
    )

    if photo_path:
        with open(photo_path, "rb") as photo_file:
            email.attach_file(photo_path, mimetype="image/jpeg")

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
    from users.models import User

    try:
        user = User.objects.get(id=user_id)

        user.balance += Decimal(value)
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
    from users.models import PhoneNumberVerifySMS

    phone_numbers = PhoneNumberVerifySMS.objects.filter(
        code=code, phone_number=phone_number
    )
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


def validate_passport_series(value):
    if not value.isdigit() or len(value) != 4:
        raise ValidationError("Invalid passport series. It must be 4 digits")


def validate_passport_number(value):
    if not value.isdigit() or len(value) != 6:
        raise ValidationError("Invalid passport number. It must be 6 digits")


def upload_media_to_yandex_cloud(self):
    if self.photo:
        # Получаем ключи доступа к Yandex.Cloud из переменных окружения
        access_key = settings.YANDEX_CLOUD_ACCESS_KEY
        secret_key = settings.YANDEX_CLOUD_SECRET_KEY
        region_name = "ru-central1-c"
        # Инициализируем клиент boto3 для работы с Yandex Object Storage
        client = boto3.client(
            "s3",
            endpoint_url="https://storage.yandexcloud.net/",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name,
        )

        # Загружаем изображение в Yandex.Cloud
        bucket_name = "solevar-bucket"
        file_path = (
            f"user_images/{self.photo.name}"  # Путь к изображению в Yandex.Cloud
        )
        file_data = self.photo.read()
        client.put_object(Bucket=bucket_name, Key=file_path, Body=file_data)

        self.photo = f"https://storage.yandexcloud.net/solevar-bucket/{file_path}"
    else:
        self.photo = f"https://storage.yandexcloud.net/solevar-bucket/user_images/no-profile.png"


def upload_audio_to_yandex_cloud(self):
    if self.record_file:
        # Получаем ключи доступа к Yandex.Cloud из переменных окружения
        access_key = settings.YANDEX_CLOUD_ACCESS_KEY
        secret_key = settings.YANDEX_CLOUD_SECRET_KEY
        region_name = "ru-central1-c"
        # Инициализируем клиент boto3 для работы с Yandex Object Storage
        client = boto3.client(
            "s3",
            endpoint_url="https://storage.yandexcloud.net/",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name,
        )

        # Загружаем изображение в Yandex.Cloud
        bucket_name = "solevar-bucket"
        file_path = (
            f"user_audio/{self.record_file.name}"  # Путь к изображению в Yandex.Cloud
        )
        file_data = self.record_file.read()
        client.put_object(Bucket=bucket_name, Key=file_path, Body=file_data)

        self.record_file = f"https://storage.yandexcloud.net/solevar-bucket/{file_path}"
    else:
        self.record_file = None
