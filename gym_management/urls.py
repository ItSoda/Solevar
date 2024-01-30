from django.urls import include, path
from rest_framework import routers

from .views import (AddOrRemoveParticipantView, BuySubscriptionView,
                    ClubViewSet, EventViewSet, IndividualEventViewSet,
                    MyEventListView, MyPassedEventViewSet, MySubscriptionView,
                    SubscriptionViewSet)

app_name = "gym_management"

router = routers.DefaultRouter()
router.register(r"clubs", ClubViewSet, basename="clubs")

urlpatterns = [
    path("", include(router.urls)),
    path("events/", EventViewSet.as_view(), name="events"),
    path("subscriptions/", SubscriptionViewSet.as_view(), name="subscriptions"),
    path(
        "individual_events/", IndividualEventViewSet.as_view(), name="individual_events"
    ),
    path("my_events/", MyEventListView.as_view(), name="my_event"),
    path("my_history_event/", MyPassedEventViewSet.as_view(), name="my_passed_event"),
    path("my_subscriptions/", MySubscriptionView.as_view(), name="my_subscriptions"),
    path("buy_subscription/", BuySubscriptionView.as_view(), name="buy_subscription"),
    path("join_event/", AddOrRemoveParticipantView.as_view(), name="join_event"),
]
