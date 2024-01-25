from django.urls import include, path
from rest_framework import routers

from .views import (AddOrRemoveParticipantView, BuySubscriptionView,
                    ClubViewSet, EventViewSet, IndividualEventViewSet,
                    MyEventListView, MySubscriptionView, SubscriptionViewSet, MyPassedEventViewSet)

app_name = "gym_management"

router = routers.DefaultRouter()
router.register(r"events", EventViewSet, basename="events")
router.register(r"clubs", ClubViewSet, basename="clubs")
router.register(r"subscriptions", SubscriptionViewSet, basename="subscriptions")
router.register(
    r"individual_events", IndividualEventViewSet, basename="individual_events"
)


urlpatterns = [
    path("", include(router.urls)),
    path("my_events/", MyEventListView.as_view(), name="my_event"),
    path("my_history_event/", MyPassedEventViewSet.as_view({"get": "list"}), name="my_passed_event"),
    path("my_subscriptions/", MySubscriptionView.as_view(), name="my_subscriptions"),
    path("buy_subscription/", BuySubscriptionView.as_view(), name="buy_subscription"),
    path(
        "join_event/<int:pk>/", AddOrRemoveParticipantView.as_view(), name="join_event"
    ),
]
