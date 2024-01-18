from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Event, Club, IndividualEvent, Subscription
from .serializers import EventCreateSerializer, EventSerializer, ClubCreateSerializer, ClubSerializer, IndividualEvent, IndividualEventSerializer
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework import status


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(limit_of_participant__gt=1)

    def create(self, request, *args, **kwargs):
        self.serializer_class = EventCreateSerializer
        return super().create(request, *args, **kwargs)
    
    def perform_update(self, serializer):
        instance = serializer.instance
        new_participants = serializer.validate_data.get("participants", instance.participants.all())

        participants_limit = instance.limit_of_participants

        if new_participants.count() > participants_limit:
            return Response({"error": "Превышен лимит участников."}, status=status.HTTP_400_BAD_REQUEST)

        super().perform_update(serializer)


class IndividualEventViewSet(ModelViewSet):
    queryset = IndividualEvent.objects.all()
    serializer_class = IndividualEventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(participant__id=self.request.user.id)
    
    def create(self, request, *args, **kwargs):
        self.serializer_class = IndividualEventSerializer
        return super().create(request, *args, **kwargs)


class ClubViewSet(ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer

    def create(self, request, *args, **kwargs):
        self.serializer_class = ClubCreateSerializer
        return super().create(request, *args, **kwargs)
    

class MyEventListView(ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(participants__id=self.request.user.id)
