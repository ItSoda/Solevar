import json
import logging

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from yookassa.domain.notification import WebhookNotificationFactory

from gym_management.permissions import IsTrainerUser

from .models import Schedule, User
from .serializers import (
    EmailContactSerializer,
    ScheduleCreateOrUpdateSerializer,
    ScheduleSerializer,
    UserInfoUpdateSerializer,
    UserShortSerializer,
)
from .services import (
    create_payment,
    proccess_phone_verification,
    send_email_from_user,
    send_phone_verify_task,
    user_change_balance,
)

logger = logging.getLogger("main")


class UserInfoUpdateAPIView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserInfoUpdateSerializer


class ScheduleModelViewSet(ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def create(self, request, *args, **kwargs):
        scheduleSerializer = ScheduleCreateOrUpdateSerializer(
            data=request.data, context={"request": request}
        )
        scheduleSerializer.validate()
        scheduleSerializer.save()

    def partial_update(self, request, *args, **kwargs):
        self.serializer_class = ScheduleCreateOrUpdateSerializer
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            instance_id = self.kwargs.get("pk")
            instance = Schedule.objects.get(id=instance_id)

            instance.delete()
            instance.save()
            return Response(
                {"message": "Delete successfully"}, status=status.HTTP_204_NO_CONTENT
            )
        except Exception:
            return Response(
                {"error": "Delete unsuccessfully"}, status=status.HTTP_400_BAD_REQUEST
            )


class IndividualEventScheduleListAPIView(ListAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        try:
            trainer_id = self.kwargs.get("trainer_id")
            trainer = User.objects.filter(id=trainer_id).first()

            if not trainer:
                return super().get_queryset()

            return Schedule.objects.filter(coach=trainer, is_selected=False)

        except Exception:
            return Response(
                {"error": "Ошибка с тренером"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TrainerScheduleListAPIView(ListAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        try:
            trainer = self.request.user

            if not trainer:
                return Response(
                    {"error": "Токен не передали."},
                )

            return Schedule.objects.filter(coach=trainer)

        except Exception:
            return Response(
                {"error": "Ошибка с тренером"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CoachListAPIView(ListAPIView):
    queryset = User.objects.filter(role="Coach")
    serializer_class = UserShortSerializer

    def get_queryset(self):
        try:
            time = self.kwargs.get("time", None)

            if not time:
                return super().get_queryset()

            schedules = Schedule.objects.get(time=time)
            return schedules.coach.all()
        except Exception:
            return Response(
                {"error": "Неправильный формат времени."},
                status=status.HTTP_400_BAD_REQUES,
            )


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


class CustomTokenObtainView(APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")
        if not phone_number:
            return Response(
                {"error": "Phone number is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )
