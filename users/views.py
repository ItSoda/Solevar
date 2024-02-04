import json
import logging

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from yookassa.domain.notification import WebhookNotificationFactory
from .models import Schedule, User
from .serializers import (EmailContactSerializer, ScheduleSerializer,
                          UserShortSerializer)
from .services import (create_payment, proccess_phone_verification,
                       send_email_from_user, send_phone_verify_task,
                       user_change_balance)
from admin_panel.serializers import ScheduleTrainerSerializer
from gym_management.permissions import IsTrainerUser

logger = logging.getLogger("main")


class ScheduleModelViewSet(ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        try:
            trainer_id = self.request.query_params.get("trainer_id", None)
            print(trainer_id)
            if not trainer_id:
                return super().get_queryset()
            print("aaaa")
            trainer = User.objects.get(User, id=trainer_id)
            return Schedule.objects.filter(coach=trainer)

        except Exception:
            return Response({"error": "Неправильный формат id тренера."}, status=status.HTTP_400_BAD_REQUEST)
    
    def create(self, request, *args, **kwargs):
        self.serializer_class = ScheduleTrainerSerializer
        return super().create(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        self.serializer_class = ScheduleTrainerSerializer
        return super().partial_update(request, *args, **kwargs)
        
    def destroy(self, request, *args, **kwargs):
        try:
            instance_id = self.request.data["schedule_id"]
            instance = Schedule.objects.filter(id=instance_id)

            instance.delete()
            instance.save()
            return Response({"message": "Delete successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response({"error": "Delete unsuccessfully"}, status=status.HTTP_400_BAD_REQUEST)


class CoachViewSet(ModelViewSet):
    queryset = User.objects.filter(role="Coach")
    serializer_class = UserShortSerializer

    @method_decorator(cache_page(10))
    def get_queryset(self):
        try:
            time = self.request.data.get("time", None)

            if not time:
                return super().get_queryset()
            
            schedules = Schedule.objects.get(time=time)
            return schedules.coach.all()
        except Exception:
            return Response({"error": "Неправильный формат времени."}, status=status.HTTP_400_BAD_REQUES)


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
                value = event_json["object"]["amount"]["value"]
                user_change_balance(user_id, value)
                return Response(
                    {"message": "Баланс успешно пополнен!"}, status=status.HTTP_200_OK
                )
        except Exception as e:
            # Обработка ошибок при разборе уведомления
            return Response(
                {"message": "Баланс не пополнен. Произошла ошибка"},
                status=status.HTTP_400_BAD_REQUEST,
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
            phone_number = request.data["phone_number"]
            send_phone_verify_task(phone_number)
            return Response({"message": "sms send success"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Произошла ошибка {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ContactEmailView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = EmailContactSerializer(data=request.data)
            if serializer.is_valid():
                # Получаем данные
                subject = request.data.get("subject")
                message = request.data.get("message")
                phone_number = request.data.get("phone_number")
                email = request.data.get("email")
                photo_path = request.data.get("photo_path", None)

                if photo_path:
                    send_email_from_user(
                        subject, message, phone_number, email, photo_path
                    )
                else:
                    send_email_from_user(subject, message, phone_number, email)
                return Response(
                    {"message": "Email send success"}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Data is not valid"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {"error": f"Произошла ошибка {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
