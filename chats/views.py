import uuid

from django.db.models import Max
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import UserSerializer

from .models import Room
from .serializers import RoomSerializer


class CreateOrGetRoomAPIView(CreateAPIView):
    serializer_class = RoomSerializer

    def post(self, request, *args, **kwargs):
        try:
            room = Room.objects.filter(
                client=f"{self.request.user.first_name} {self.request.user.last_name} {self.request.user.id}"
            ).first()
            first_name = self.request.user.first_name
            if not room:
                user = self.request.user
                username = f"{user.first_name} {user.last_name} {user.id}"
                room_uuid = uuid.uuid4()

                Room.objects.create(uuid=room_uuid, client=username)
                return Response(
                    {"uuid": room_uuid, "name": first_name},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"uuid": room.uuid, "name": first_name},
                    status=status.HTTP_201_CREATED,
                )
        except Exception as e:
            return Response({"error": f"Error: {str(e)}"})


class ChatAdminListAPIView(ListAPIView):
    serializer_class = RoomSerializer

    def get_queryset(self):
        return Room.objects.annotate(
            last_message_time=Max("messages__created_at")
        ).order_by("-last_message_time")


class FullAdminListAPIView(ListAPIView):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = UserSerializer


class GetRoomAPIView(RetrieveAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get(self, request, *args, **kwargs):
        try:
            uuid = self.kwargs.get("uuid")
            room = Room.objects.get(uuid=uuid)
            admin_name = self.request.user.first_name

            if room.status == Room.WAITING:
                room.status = Room.ACTIVE
                room.save()

            return Response({"name": admin_name}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Room not found"}, status=status.HTTP_404_NOT_FOUND
            )
