from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Event
from .serializers import EventCreateSerializer, EventSerializer
from rest_framework.generics import ListAPIView

class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def create(self, request, *args, **kwargs):
        self.serializer_class = EventCreateSerializer
        return super().create(request, *args, **kwargs)
    

class MyEventListView(ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(participants__id=self.request.user.id)
