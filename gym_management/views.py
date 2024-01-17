from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Event
from .serializers import EventCreateSerializer, EventSerializer


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def create(self, request, *args, **kwargs):
        self.serializer_class = EventCreateSerializer
        return super().create(request, *args, **kwargs)
