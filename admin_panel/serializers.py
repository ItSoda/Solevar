from rest_framework import serializers

from gym_management.models import Event, IndividualEvent, Subscription, Tag
from gym_management.serializers import TagSerializer
from users.models import Schedule, User
from users.serializers import ImageFieldFromURL


class ScheduleAdminSerializer(serializers.ModelSerializer):
    times = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Schedule
        fields = ("times",)


class TrainerAdminCreateOrUpdateSerializer(serializers.ModelSerializer):
    times = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = User
        fields = "all"

    def create(self, validated_data):
        times_ids = validated_data.pop("times")

        instance = User.objects.create_user(**validated_data)
        instance.times.set(times_ids)

        return instance

    def update(self, instance, validated_data):
        times_ids = validated_data.pop("times", None)

        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.patronymic = validated_data.get("patronymic", instance.patronymic)
        instance.email = validated_data.get("email", instance.email)
        instance.description = validated_data.get("description", instance.description)
        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.role = validated_data.get("role", instance.role)
        instance.balance = validated_data.get("balance", instance.balance)
        instance.rating = validated_data.get("rating", instance.rating)
        instance.trainer_type = validated_data.get(
            "trainer_type", instance.trainer_type
        )
        instance.is_verified_email = validated_data.get(
            "is_verified_email", instance.is_verified_email
        )

        instance.save()

        if times_ids is not None:
            instance.times.set(times_ids)

        return instance


class TrainerAdminSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    times = ScheduleAdminSerializer(many=True)
    photo = ImageFieldFromURL()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "is_verified_email",
            "password",
            "first_name",
            "last_name",
            "patronymic" "is_verified_email",
            "description",
            "photo",
            "phone_number",
            "role",
            "balance",
            "rating",
            "trainer_type",
            "date_joined",
            "last_login",
            "is_staff",
        )
        read_only_fields = ("password", "date_joined", "last_login")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.photo:
            representation["photo"] = "http://fohowomsk.ru/media/" + str(instance.photo)
        return representation


class UserAdminSerializer(serializers.ModelSerializer):
    photo = ImageFieldFromURL()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "is_verified_email",
            "password",
            "first_name",
            "last_name",
            "patronymic",
            "is_verified_email",
            "description",
            "photo",
            "phone_number",
            "role",
            "balance",
            "date_joined",
            "last_login",
            "is_staff",
            "date_of_birth",
        )
        read_only_fields = ("password", "date_joined", "last_login")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.photo:
            representation["photo"] = "http://onlydev.fun/media/" + str(instance.photo)
        return representation


class EventAdminCreateOrUpdateSerializer(serializers.ModelSerializer):
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

        participants_ids = validated_data.pop("participants")
        tags_ids = validated_data.pop("tags")

        instance = Event.objects.create(
            created_by=created_by_instance, **validated_data
        )
        instance.participants.set(participants_ids)
        instance.tags.set(tags_ids)

        return instance

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


class IndividualEventAdminCreateOrUpdateSerializer(serializers.ModelSerializer):
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

    def update(self, instance, validated_data):
        # Обновление полей IndividualEvent
        instance.description = validated_data.get("description", instance.description)
        instance.duration = validated_data.get("duration", instance.duration)
        instance.quantity = validated_data.get("quantity", instance.quantity)
        instance.price = validated_data.get("price", instance.price)

        coach_id = validated_data.get("coach", None)
        if coach_id is not None:
            coach = User.objects.get(id=coach_id)
            instance.coach = coach

        training_date = validated_data.get("training_date", None)
        if training_date is not None:
            instance.training_date = training_date

        instance.save()

        return instance


class SubscriptionAdminCreateOrUpdateSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(write_only=True)

    class Meta:
        model = Subscription
        fields = "__all__"

    def create(self, validated_data):
        user_id = validated_data.pop("user")
        user = User.objects.get(id=user_id)

        instance = Subscription.objects.create(user=user, **validated_data)

        return instance

    def update(self, instance, validated_data):
        # Обновление полей Subscription
        instance.duration = validated_data.get("duration", instance.duration)
        instance.price = validated_data.get("price", instance.price)
        # Добавьте другие поля по аналогии

        user_id = validated_data.get("user", None)
        if user_id is not None:
            user = User.objects.get(id=user_id)
            instance.user = user

        instance.save()

        return instance
