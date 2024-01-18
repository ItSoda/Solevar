from rest_framework import serializers
from .models import Event, Tag, Club, IndividualEvent

from users.models import User
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class EventCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.IntegerField(write_only=True)
    club = serializers.IntegerField(write_only=True)
    participants = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    tags = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    
    class Meta:
        model = Event
        fields = "__all__"

    def create(self, validated_data):
        created_by_id = validated_data.pop("created_by")
        created_by_instance = User.objects.get(id=created_by_id)

        club_id = validated_data.pop("club")
        club_instance = Club.objects.get(id=club_id)

        participants_ids = validated_data.pop("participants")
        tags_ids = validated_data.pop("tags")

        instance = Event.objects.create(club=club_instance, created_by=created_by_instance, **validated_data)
        instance.participants.set(participants_ids)
        instance.tags.set(tags_ids)

        return instance


class EventSerializer(serializers.ModelSerializer):
    created_by = UserSerializer()
    participants = UserSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Event
        fields = "__all__"


class ClubCreateSerializer(serializers.ModelSerializer):
    coaches = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    
    class Meta:
        model = Club
        fields = "__all__"

    def create(self, validated_data):
        coaches_ids = validated_data.pop("coaches")

        instance = Club.objects.create(**validated_data)
        instance.coaches.set(coaches_ids)

        return instance


class ClubSerializer(serializers.ModelSerializer):
    coaches = UserSerializer(many=True)

    class Meta:
        model = Club
        fields = "__all__"


class IndividualEventCreateSerializer(serializers.ModelSerializer):
    coach = serializers.IntegerField(write_only=True)
    participant = serializers.IntegerField(write_only=True)

    class Meta:
        model = IndividualEvent
        fields = "__all__"

    def create(self, validated_data):
        coach_id = validated_data.pop("coach")
        coach = User.objects.get(id=coach_id)

        participant_id = validated_data.pop("participant")
        participant = User.objects.get(id=participant_id)

        instance = IndividualEvent.objects.create(coach=coach, participant=participant, **validated_data)

        return instance


class IndividualEventSerializer(serializers.ModelSerializer):
    coach = UserSerializer()
    participant = UserSerializer()

    class Meta:
        model = IndividualEvent
        fields = "__all__"