from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import User
from .serializers import UserShortSerializer


class CoachViewSet(ModelViewSet):
    queryset = User.objects.filter(role="Coach")
    serializer_class = UserShortSerializer

