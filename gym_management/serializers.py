from rest_framework import serializers
from .models import Event, Tag

from users.models import User
from users.serializers import UserSerializer

class EventCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.IntegerField(write_only=True)
    participants = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    tags = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    
    class Meta:
        model = Event
        fields = "__all__"

    def create(self, validated_data):
        created_by_id = validated_data.pop("created_by")
        created_by_instance = User.objects.get(id=created_by_id)

        participants_ids = validated_data.pop("participants")
        tags_ids = validated_data.pop("tags")

        instance = Event.objects.create(created_by=created_by_instance, **validated_data)
        instance.participants.set(participants_ids)
        instance.tags.set(tags_ids)

        return instance


class EventSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Event
        fields = "__all__"
