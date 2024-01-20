import json

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from yookassa.domain.notification import WebhookNotificationFactory

from .models import User
from .serializers import UserShortSerializer
from .services import (create_payment, proccess_phone_verification,
                       send_phone_verify_task, user_change_balance)


class CoachViewSet(ModelViewSet):
    queryset = User.objects.filter(role="Coach")
    serializer_class = UserShortSerializer

    @method_decorator(cache_page(10))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class YookassaPaymentView(APIView):
    def post(self, request):
        user = self.request.user

        email = request.data.get("email")
        amount = request.data.get("amount")

        if not email or not amount:
            return Response(
                {"error": "Почта и сумма обязательны."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Обьект платежа
        payment_url = create_payment(email, amount, user, request)

        # Перенаправка пользователя на страницу оплаты Юкассы
        return Response(
            {
                "payment_url": payment_url,
            },
            status=status.HTTP_200_OK,
        )


class YookassaWebhookView(APIView):
    def post(self, request):
        event_json = json.loads(request.body.decode("utf-8"))
        user_id = event_json["object"]["metadata"].get("userId")
        try:
            notification = WebhookNotificationFactory().create(event_json)
            # Проверяем статус платежа
            if notification.object.status == "succeeded":
                # Обновляем баланс
                user_change_balance(user_id, notification)
        except Exception as e:
            # Обработка ошибок при разборе уведомления
            return Response(
                {"message": "Баланс пополнен. Произошла ошибка"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"message": "Баланс успешно пополнен!"}, status=status.HTTP_200_OK
        )


class PhoneNumberVerificationView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Получаем данные
            phone_number = request.data.get("phone_number")
            code = request.data.get("code")

            phone_verify_result = proccess_phone_verification(code, phone_number)

            if phone_verify_result:
                return Response(
                    {"message": "Phone number success"}, status=status.HTTP_200_OK
                )
            return Response(
                {"message": "Phone number is expired or not exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"error": "Произошла ошибка"}, status=status.HTTP_400_BAD_REQUEST
            )


class PhoneNumberSendSMSView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Получаем данные
            phone_number = request.data.get("phone_number")
            send_phone_verify_task(phone_number)
            return Response({"message": "sms send success"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Произошла ошибка {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
