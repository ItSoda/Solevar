from django.forms import ValidationError
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from decimal import Decimal
from random import randint
from .models import Club, Event, IndividualEvent, Subscription
from .serializers import (ClubCreateSerializer, ClubSerializer,
                          EventCreateSerializer, EventSerializer,
                          IndividualEventCreateSerializer,
                          IndividualEventSerializer,
                          SubscriptionCreateSerializer, SubscriptionSerializer)


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(limit_of_participants__gt=1)

    @method_decorator(cache_page(10))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self.serializer_class = EventCreateSerializer
        return super().create(request, *args, **kwargs)

    def perform_update(self, serializer):
        instance = serializer.instance
        new_participants = serializer.validate_data.get(
            "participants", instance.participants.all()
        )

        participants_limit = instance.limit_of_participants

        if new_participants.count() > participants_limit:
            return Response(
                {"error": "Превышен лимит участников."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        super().perform_update(serializer)


class IndividualEventViewSet(ModelViewSet):
    queryset = IndividualEvent.objects.all()
    serializer_class = IndividualEventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(participant=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            self.serializer_class = IndividualEventCreateSerializer
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ClubViewSet(ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer

    @method_decorator(cache_page(10))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self.serializer_class = ClubCreateSerializer
        return super().create(request, *args, **kwargs)


class MyEventListView(ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(participants__id=self.request.user.id)


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

                return Response({"message": "Buy Subscription success"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

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
