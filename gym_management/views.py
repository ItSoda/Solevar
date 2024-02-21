from decimal import Decimal
from random import randint

from django.db.utils import IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q
from gym_management.services import (
    add_user_to_event,
    change_time_selected,
    down_user_balance,
    remove_user_from_event,
)
from gym_management.tasks import send_email_succes_buy_personal_trainer

from .models import Event, IndividualEvent, Subscription, Tag
from .permissions import IsTrainerUser
from .serializers import (
    EventCreateSerializer,
    EventSerializer,
    IndividualEventCreateSerializer,
    IndividualEventSerializer,
    SubscriptionSerializer,
    TagSerializer,
    TrainerEventUpdateSerializer,
    EventCreateSerializer,
)


class MainEventListAPIView(ListAPIView):
    queryset = Event.objects.filter(Q(status="WAITING") | Q(status="EDIT"))
    serializer_class = EventSerializer

    @method_decorator(cache_page(10))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


# Групповые тренировки
class EventViewSet(ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @method_decorator(cache_page(10))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AddOrRemoveParticipantView(UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventCreateSerializer

    def put(self, request, *args, **kwargs):
        try:
            user = self.request.user
            event_id = request.data["pk"]
            event = Event.objects.get(id=event_id)

            if user.id not in event.participants.all().values_list("id", flat=True):
                # Пользователь был не записан
                if event.participants.count() + 1 <= event.limit_of_participants:
                    if user.balance >= event.price:
                        # Добавление пользователя
                        add_user_to_event(event, user)
                        return Response(
                            {"message": "Participant added"}, status=status.HTTP_200_OK
                        )
                    else:
                        return Response(
                            {"error": "Not enough money"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                else:
                    return Response(
                        {"error": "Too many participants"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                # Пользователь был записан на этот ивент, поэтому удаляем его
                remove_user_from_event(event, user)
                return Response(
                    {"message": "Participant removed and funds returned"},
                    status=status.HTTP_200_OK,
                )

        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Data is not valid: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MyEventListView(ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(participants__id=self.request.user.id, status="WAITING")


class MyHistoryEventListView(ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(participants=self.request.user, status="PASSED")


# Персональные тренировки
class IndividualEventViewSet(CreateAPIView):
    queryset = IndividualEvent.objects.all()
    serializer_class = IndividualEventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(participant=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            # Получение данных
            user = self.request.user
            price = request.data["price"]
            training_date = request.data["training_date"]
            coach = request.data["coach"]

            # Создание события без сохранения в базу данных
            event_serializer = IndividualEventCreateSerializer(
                data=request.data, context={"request": request}
            )
            event_serializer.is_valid(raise_exception=True)

            if user.balance >= Decimal(price):
                event_serializer.save()
                # Уменьшение баланса
                change_time_selected(training_date, coach)
                down_user_balance(user, price)
                send_email_succes_buy_personal_trainer.delay(
                    user.email,
                    user.first_name,
                    request.data["coach"],
                    request.data["training_date"],
                )

                return Response(
                    {"message": "Success buy individual event"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"error": "Not enough money or individual event already create"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except IntegrityError as e:
            return Response(
                {"error": "Duplicate entry"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MyIndividualEventListAPIView(ListAPIView):
    serializer_class = IndividualEventSerializer

    def get_queryset(self):
        return IndividualEvent.objects.filter(participant=self.request.user)

    @method_decorator(cache_page(10))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


# Абонементы
class SubscriptionViewSet(ListAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    @method_decorator(cache_page(10))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class BuySubscriptionView(CreateAPIView):
    serializer_class = SubscriptionSerializer
    def post(self, request, *args, **kwargs):
        try:
            number = self.generate_unique_subscription_number()

            price = request.data.get("price")
            duration = request.data.get("duration")
            user = self.request.user

            if user.balance >= Decimal(price):
                down_user_balance(user, price)

                subscription = Subscription.objects.create(
                    price=price, user=user, duration=duration, number=number
                )

                return Response(
                    {"message": "Buy Subscription success"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"error": "Insufficient balance"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def generate_unique_subscription_number(self):
        while True:
            number = randint(1000000000, 9999999999)
            if not Subscription.objects.filter(number=number).exists():
                return number


class MySubscriptionView(ListAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


# Trainer Panel - Method
class TrainerEventModelViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        trainer_event_serializer = EventCreateSerializer(
            data=request.data, context={"request": request}
        )
        trainer_event_serializer.is_valid(raise_exception=True)
        trainer_event_serializer.save()
        return Response(
            {"message": "Event create success"}, status=status.HTTP_201_CREATED
        )

    def partial_update(self, request, *args, **kwargs):
        self.serializer_class = TrainerEventUpdateSerializer
        return super().partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.serializer_class = TrainerEventUpdateSerializer
        return super().update(request, *args, **kwargs)


class TrainerIndividualEventAPIView(ListAPIView):
    queryset = IndividualEvent.objects.all()
    serializer_class = IndividualEventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(coach=self.request.user)


class TrainerUpdateQuantityIndividualEventAPIView(UpdateAPIView):
    queryset = IndividualEvent.objects.all()
    serializer_class = IndividualEventSerializer


class TrainerTagAPIView(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
