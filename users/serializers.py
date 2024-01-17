from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from django.core.files import File

from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from .models import User


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
        fields = ("id", "photo", "first_name", "last_name", "description", "rating")
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.photo:
            representation['photo'] = "http://red-store.site/media/" + str(instance.photo)
        return representation


class UserProfile(UserSerializer):
    photo = ImageFieldFromURL()
    
    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "password",
            "username",
            "first_name",
            "last_name",
            "is_verified_email",
            "description",
            "photo",
            "phone_number",
            "role",
        )
        read_only_fields = ("password",)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.photo:
            representation['photo'] = "http://red-store.site/media/" + str(instance.photo)
        return representation