from django.forms import ValidationError
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

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
        self.serializer_class = IndividualEventCreateSerializer
        return super().create(request, *args, **kwargs)


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
            serializer = SubscriptionCreateSerializer(data=request.data)
            if serializer.is_valid():
                # Получаем данные
                price = request.data.get("price")
                user = self.request.user
            print(user.id)
            if int(user.balance) >= int(price):
                user.balance -= int(price)
                user.save()
                return Response({"message": "Buy Subscription success"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Balance is not valid"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Произошла ошибка {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MySubscriptionView(ListAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)
