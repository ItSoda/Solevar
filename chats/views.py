from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from users.models import User
from users.serializers import UserSerializer

from .models import Room
from .serializers import RoomSerializer
import uuid


class CreateRoomCreateAPIView(CreateAPIView):
    def post(self, request, *args, **kwargs):
        try:
            user = self.request.user
            username = f"{user.first_name} {user.last_name}"
            room_uuid = uuid.uuid4()

            Room.objects.create(uuid=room_uuid, client=username)
            return Response({"data": room_uuid}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"Error: {str(e)}"})


class ChatAdminListAPIView(ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class FullAdminListAPIView(ListAPIView):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = UserSerializer


class GetRoomRetrieveAPIView(RetrieveAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get(self, request, *args, **kwargs):
        try:
            uuid = self.kwargs.get("uuid")
            room = Room.objects.get(uuid=uuid)

            if room.status == Room.WAITING:
                room.status = Room.ACTIVE
                room.agent = self.request.user
                room.save()

            return Response({"message": "Вы успешно вошли!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Room not found"}, status=status.HTTP_404_NOT_FOUND
            )