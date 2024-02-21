from rest_framework import serializers

from users.models import User
from users.serializers import UserMinSerializer

from .models import Event, IndividualEvent, Subscription, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class EventCreateSerializer(serializers.ModelSerializer):
    participants = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    tags = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    start_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Event
        fields = "__all__"

    def create(self, validated_data):
        created_by_instance = self.context["request"].user
        participants_ids = validated_data.pop("participants")
        tags_ids = validated_data.pop("tags")

        instance = Event.objects.create(
            created_by=created_by_instance, **validated_data
        )
        instance.participants.set(participants_ids)
        instance.tags.set(tags_ids)

        return instance


class EventSerializer(serializers.ModelSerializer):
    seats_left = serializers.SerializerMethodField()
    created_by = UserMinSerializer()
    participants = UserMinSerializer(many=True)
    tags = TagSerializer(many=True)
    start_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Event
        fields = "__all__"

    def get_seats_left(self, obj):
        return obj.seats_left()


class TrainerEventUpdateSerializer(serializers.ModelSerializer):
    participants = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    tags = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    start_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Event
        fields = "__all__"

    def update(self, instance, validated_data):
        created_by_id = validated_data.pop("created_by", None)
        participants_ids = validated_data.pop("participants", None)
        tags_ids = validated_data.pop("tags", None)

        # Обновление полей Event
        instance.title = validated_data.get("title", instance.title)
        instance.content = validated_data.get("content", instance.content)
        instance.limit_of_participants = validated_data.get(
            "limit_of_participants", instance.limit_of_participants
        )
        instance.start_date = validated_data.get("start_date", instance.start_date)
        instance.duration = validated_data.get("duration", instance.duration)
        instance.club = validated_data.get("club", instance.club)
        instance.price = validated_data.get("price", instance.price)
        instance.status = validated_data.get("status", instance.status)

        instance.save()

        if created_by_id is not None:
            created_by_instance = User.objects.get(id=created_by_id)
            instance.created_by = created_by_instance

        if participants_ids is not None:
            instance.participants.set(participants_ids)

        if tags_ids is not None:
            instance.tags.set(tags_ids)

        return instance


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
    coach = UserMinSerializer()
    participant = UserMinSerializer()
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
    user = UserMinSerializer()
    start_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Subscription
        fields = "__all__"
