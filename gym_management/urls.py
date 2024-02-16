from django.urls import include, path
from rest_framework import routers

from .views import (AddOrRemoveParticipantView, BuySubscriptionView,
                    EventViewSet, IndividualEventViewSet, MainEventListAPIView,
                    MyEventListView, MyHistoryEventListView,
                    MyIndividualEventListAPIView, MySubscriptionView,
                    SubscriptionViewSet, TrainerEventModelViewSet,
                    TrainerIndividualEventAPIView, TrainerTagAPIView, TrainerUpdateQuantityIndividualEventAPIView)

app_name = "gym_management"

router = routers.DefaultRouter()
router.register(r"trainer_events", TrainerEventModelViewSet, basename="trainer_events")
router.register(r"tags", TrainerTagAPIView, basename="tags")

urlpatterns = [
    path("", include(router.urls)),
    path("main_events/", MainEventListAPIView.as_view(), name="main_events"),
    path(
        "my_history_events/", MyHistoryEventListView.as_view(), name="my_history_events"
    ),
    path("events/", EventViewSet.as_view(), name="events"),
    path("subscriptions/", SubscriptionViewSet.as_view(), name="subscriptions"),
    path(
        "create/individual_events/",
        IndividualEventViewSet.as_view(),
        name="individual_events",
    ),
    path(
        "my_individual_events/",
        MyIndividualEventListAPIView.as_view(),
        name="my_individual_events",
    ),
    path("my_events/", MyEventListView.as_view(), name="my_event"),
    path("my_subscriptions/", MySubscriptionView.as_view(), name="my_subscriptions"),
    path("buy_subscription/", BuySubscriptionView.as_view(), name="buy_subscription"),
    path("join_event/", AddOrRemoveParticipantView.as_view(), name="join_event"),
    path(
        "trainer_list_individual_event/",
        TrainerIndividualEventAPIView.as_view(),
        name="trainer-list-individual-event",
    ),
    path("trainer_update_individual_event/<int:pk>/", TrainerUpdateQuantityIndividualEventAPIView.as_view(), name="trainer_update_individual_event"),
    path(
        "my_history_events/", MyHistoryEventListView.as_view(), name="my_history_events"
    ),
]
