import datetime
from decimal import Decimal
from random import randint

from django.forms import ValidationError
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db.utils import IntegrityError
from gym_management.tasks import (send_email_join_success_task,
                                  send_email_leave_success_task, send_email_succes_buy_personal_trainer)

from .models import Club, Event, IndividualEvent, Subscription
from .serializers import (ClubCreateSerializer, ClubSerializer,
                          EventCreateSerializer, EventSerializer,
                          IndividualEventCreateSerializer,
                          IndividualEventSerializer,
                          SubscriptionCreateSerializer, SubscriptionSerializer)


# Групповые тренировки
class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @method_decorator(cache_page(10))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self.serializer_class = EventCreateSerializer
        return super().create(request, *args, **kwargs)


class AddOrRemoveParticipantView(UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventCreateSerializer

    def put(self, request, *args, **kwargs):
        try:
            user = self.request.user
            event_id = kwargs.get("pk")
            event = Event.objects.get(id=event_id)

            if user.id not in event.participants.all().values_list("id", flat=True):
                # Пользователь был не записан
                if event.participants.count() + 1 <= event.limit_of_participants:
                    if user.balance >= event.price:
                        event.participants.add(user)
                        user.balance -= event.price
                        user.save()
                        event.save()
                        send_email_join_success_task.delay(
                            user.email, user.first_name, event.id
                        )
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
                # Пользователь был записан
                event.participants.remove(user)
                user.balance += event.price
                user.save()
                event.save()
                send_email_leave_success_task.delay(
                    user.email, user.first_name, event.id
                )
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
        return queryset.filter(participants__id=self.request.user.id)


# История посещения групповых тренировок
class MyPassedEventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(participants=self.request.user, status="Passed")
    
    def create(self, request, *args, **kwargs):
        self.serializer_class = EventCreateSerializer
        return super().create(request, *args, **kwargs)


# Персональные тренировки
class IndividualEventViewSet(ModelViewSet):
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

            # Создание события без сохранения в базу данных
            event_serializer = IndividualEventCreateSerializer(data=request.data, context={"request": request})
            event_serializer.is_valid(raise_exception=True)

            if user.balance >= Decimal(price):
                event_serializer.save()
                # Уменьшение баланса
                user.balance -= Decimal(price)
                user.save()
                send_email_succes_buy_personal_trainer.delay(user.email, user.first_name, request.data["coach"], request.data["training_date"])

                return Response(event_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"error": "Not enough money or individual event already create"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except IntegrityError as e:
            return Response({"error": "Duplicate entry"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Клубы
class ClubViewSet(ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer

    @method_decorator(cache_page(10))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self.serializer_class = ClubCreateSerializer
        return super().create(request, *args, **kwargs)


# Абонементы
class SubscriptionViewSet(ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    @method_decorator(cache_page(10))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self.serializer_class = SubscriptionCreateSerializer
        return super().create(request, *args, **kwargs)


class BuySubscriptionView(CreateAPIView):
    def post(self, request, *args, **kwargs):
        try:
            number = self.generate_unique_subscription_number()

            price = request.data.get("price")
            duration = request.data.get("duration")
            user = self.request.user

            if user.balance >= Decimal(price):
                user.balance -= Decimal(price)
                user.save()

                subscription = Subscription.objects.create(
                    price=price, user=user, duration=duration, number=number
                )

                return Response(
                    {"message": "Buy Subscription success"}, status=status.HTTP_200_OK
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

