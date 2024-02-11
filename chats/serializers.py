from rest_framework import serializers

from users.models import User
from users.serializers import UserSerializer

from .models import Message, Room


class MessageSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Message
        fields = "__all__"


class RoomSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    agent = UserSerializer()

    class Meta:
        model = Room
        fields = "__all__"
        read_only_fields = [
            "messages",
        ]