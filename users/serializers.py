from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from django.core.files import File
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import Schedule, User


class ImageFieldFromURL(serializers.ImageField):
    def to_internal_value(self, data):
        # Проверяем, если data - это URL
        if data.startswith("http") or data.startswith("https"):
            # Открываем URL и читаем его содержимое
            response = urlopen(data)
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(response.read())
            img_temp.flush()
            # Создаем объект File из временного файла
            img = File(img_temp)
            # Возвращаем его как значение поля
            return img
        return super().to_internal_value(data)


class UserRegistSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ("id", "phone_number", "password")


class UserShortSerializer(UserSerializer):
    photo = ImageFieldFromURL()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            "id",
            "photo",
            "first_name",
            "last_name",
            "patronymic",
            "description",
            "rating",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.photo:
            representation["photo"] = "http://fohowomsk.ru/media/" + str(instance.photo)
        return representation


class UserProfile(UserSerializer):
    event_history = serializers.SerializerMethodField()
    photo = ImageFieldFromURL()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "is_verified_email",
            "date_of_birth",
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
            "is_staff",
            "event_history"
        )
        read_only_fields = ("password",)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.photo:
            representation["photo"] = "http://fohowomsk.ru/media/" + str(instance.photo)
        return representation
    
    def get_event_history(self, obj):
        return obj.event_history()


class EmailContactSerializer(serializers.Serializer):
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=100)
    message = serializers.CharField()


class ScheduleCreateOrUpdateSerializer(serializers.ModelSerializer):
    coach = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Schedule
        fields = "__all__"

    def create(self, validated_data):
        coach_id = validated_data.pop("coach")

        instance = Schedule.objects.create(**validated_data)
        instance.coach.set(coach_id)

        return instance

    def update(self, instance, validated_data):
        coach = validated_data.pop("coach", None)

        instance.time = validated_data.get("time", instance.time)
        instance.is_selected = validated_data.get("is_selected", instance.is_selected)

        instance.save()

        if coach is not None:
            instance.coach.set(coach)

        return instance


class ScheduleSerializer(serializers.ModelSerializer):
    time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    coach = UserShortSerializer(many=True)

    class Meta:
        model = Schedule
        fields = "__all__"
