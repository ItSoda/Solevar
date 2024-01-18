from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Event, Club
from .serializers import EventCreateSerializer, EventSerializer, ClubCreateSerializer, ClubSerializer
from rest_framework.generics import ListAPIView

class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def create(self, request, *args, **kwargs):
        self.serializer_class = EventCreateSerializer
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
