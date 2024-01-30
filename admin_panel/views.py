from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from admin_panel.serializers import (
    EventAdminCreateOrUpdateSerializer,
    IndividualEventAdminCreateOrUpdateSerializer,
    SubscriptionAdminCreateOrUpdateSerializer,
    TrainerAdminCreateOrUpdateSerializer, TrainerAdminSerializer,
    UserAdminSerializer)
from gym_management.models import Event, IndividualEvent, Subscription
from gym_management.serializers import (EventSerializer,
                                        IndividualEventSerializer,
                                        SubscriptionSerializer)
from users.models import User


# Пользователи и тренера
class UserAdminViewSet(ModelViewSet):
    queryset = User.objects.filter(role="Client")
    serializer_class = UserAdminSerializer
    permission_classes = (IsAdminUser,)


class TrainerAdminViewSet(ModelViewSet):
    queryset = User.objects.filter(role="Coach")
    serializer_class = TrainerAdminCreateOrUpdateSerializer
    permission_classes = (IsAdminUser,)

    def list(self, request, *args, **kwargs):
        self.serializer_class = TrainerAdminSerializer
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = TrainerAdminSerializer
        return super().retrieve(request, *args, **kwargs)


# Групповые тренировки
class EventAdminViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventAdminCreateOrUpdateSerializer
    permission_classes = (IsAdminUser,)

    def list(self, request, *args, **kwargs):
        self.serializer_class = EventSerializer
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = EventSerializer
        return super().retrieve(request, *args, **kwargs)


# Персональные тренировки
class IndividualEventAdminViewSet(ModelViewSet):
    queryset = IndividualEvent.objects.all()
    serializer_class = IndividualEventAdminCreateOrUpdateSerializer
    permission_classes = (IsAdminUser,)

    def list(self, request, *args, **kwargs):
        self.serializer_class = IndividualEventSerializer
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = IndividualEventSerializer
        return super().retrieve(request, *args, **kwargs)


class SubscriptionAdminViewSet(ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionAdminCreateOrUpdateSerializer
    permission_classes = (IsAdminUser,)

    def list(self, request, *args, **kwargs):
        self.serializer_class = SubscriptionSerializer
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = SubscriptionSerializer
        return super().retrieve(request, *args, **kwargs)
