from django.urls import include, path
from rest_framework import routers

from .views import (ClubViewSet, EventViewSet, IndividualEventViewSet,
                    MyEventListView, SubscriptionViewSet, MySubscriptionView)

app_name = "gym_management"

router = routers.DefaultRouter()
router.register(r"events", EventViewSet, basename="events")
router.register(r"clubs", ClubViewSet, basename="clubs")
router.register(r"subscriptions", SubscriptionViewSet, basename="subscriptions")
router.register(r"individual_events", IndividualEventViewSet, basename="individual_events")

urlpatterns = [
    path("", include(router.urls)),
    path("myevents/", MyEventListView.as_view(), name="myevent"),
    path("my_subscriptions/", MySubscriptionView.as_view(), name="my_subscriptions"),
]
