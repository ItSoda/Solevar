from rest_framework import serializers

from users.models import User
from users.serializers import UserSerializer

from .models import Club, Event, IndividualEvent, Subscription, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class EventCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.IntegerField(write_only=True)
    club = serializers.IntegerField(write_only=True)
    participants = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    tags = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    start_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

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

        instance = Event.objects.create(
            club=club_instance, created_by=created_by_instance, **validated_data
        )
        instance.participants.set(participants_ids)
        instance.tags.set(tags_ids)

        return instance


class EventSerializer(serializers.ModelSerializer):
    seats_left = serializers.SerializerMethodField()
    created_by = UserSerializer()
    participants = UserSerializer(many=True)
    tags = TagSerializer(many=True)
    start_date = serializers.DateTimeField(format="%H:%M")

    class Meta:
        model = Event
        fields = "__all__"

    def get_seats_left(self, obj):
        return obj.seats_left()


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
    training_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = IndividualEvent
        fields = (
            "coach",
            "training_date",
            "description",
            "duration",
            "quantity",
            "price",
        )

    def create(self, validated_data):
        coach_id = validated_data.pop("coach")
        coach = User.objects.get(id=coach_id)

        participant = self.context["request"].user

        instance = IndividualEvent.objects.create(
            coach=coach, participant=participant, **validated_data
        )

        return instance


class IndividualEventSerializer(serializers.ModelSerializer):
    coach = UserSerializer()
    participant = UserSerializer()
    training_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = IndividualEvent
        fields = "__all__"


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(write_only=True)

    class Meta:
        model = Subscription
        fields = "__all__"

    def create(self, validated_data):
        user_id = validated_data.pop("user")
        user = User.objects.get(id=user_id)

        instance = Subscription.objects.create(user=user, **validated_data)

        return instance


class SubscriptionSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    start_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Subscription
        fields = "__all__"
