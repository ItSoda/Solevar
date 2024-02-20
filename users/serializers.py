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
            "trainer_type",
        )


class UserMinSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
        )


class UserProfile(UserSerializer):
    date_of_issue = serializers.DateField(format="%Y-%m-%d")
    date_of_birth = serializers.DateField(format="%Y-%m-%d")
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
            "passport_series",
            "passport_number",
            "date_of_issue",
            "place_of_issue",
            "registration_address",
        )
        read_only_fields = ("password",)


class UserInfoUpdateSerializer(serializers.ModelSerializer):
    date_of_issue = serializers.DateField(format="%Y-%m-%d")
    date_of_birth = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "date_of_birth",
            "first_name",
            "last_name",
            "patronymic",
            "passport_series",
            "passport_number",
            "date_of_issue",
            "place_of_issue",
            "registration_address",
        )


class EmailContactSerializer(serializers.Serializer):
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=100)
    message = serializers.CharField()


class ScheduleCreateOrUpdateSerializer(serializers.ModelSerializer):
    time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Schedule
        fields = ("time",)

    def create(self, validated_data):
        coach_id = self.context["request"].user.id

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
    coach = UserMinSerializer(many=True)

    class Meta:
        model = Schedule
        fields = "__all__"
