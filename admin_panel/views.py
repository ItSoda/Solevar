from rest_framework.viewsets import ModelViewSet
from admin_panel.serializers import UserAdminSerializer
from users.models import User
from gym_management.serializers import EventSerializer, IndividualEventSerializer, TagSerializer, ClubSerializer, SubscriptionSerializer
from gym_management.models import Event, IndividualEvent, Tag, Club, Subscription
from rest_framework.views import APIView


class UserAdminViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer

    
class EventAdminViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class IndividualEventAdminViewSet(ModelViewSet):
    queryset = IndividualEvent.objects.all()
    serializer_class = IndividualEventSerializer


class TagAdminViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ClubAdminViewSet(ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer


class SubscriptionAdminViewSet(ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer