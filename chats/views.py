from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User

from .models import Room
from .serializers import RoomCreateSerializer, RoomSerializer
import uuid

class CreateRoom(APIView):
    serializer_class = RoomCreateSerializer

    def get(self, request, uuid):
        try:
            room_uuid = uuid.uuid4()
            user = self.request.user
            username = user.first_name + user.last_name

            Room.objects.create(uuid=room_uuid, client=username)

            return Response({"data": room_uuid}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"data": f"error - {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )


class ChatAdmin(APIView):
    serializer_class = RoomSerializer

    def get(self, request, *args, **kwargs):
        try:
            rooms = Room.objects.all()
            users = User.objects.filter(is_stuff=True)

            return Response({"rooms": rooms, "users": users}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"data": f"error - {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )


class Room(APIView):
    serializer_class = RoomSerializer

    def get(self, request, uuid, *args, **kwargs):
        try:
            room = Room.objects.get(uuid=uuid)

            if room.status == Room.WAITING:
                room.status = Room.ACTIVE
                room.agent = self.request.user
                room.save()

            return Response({"room": room}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"data": f"error - {str(e)}"}, status=status.HTTP_404_NOT_FOUND
            )