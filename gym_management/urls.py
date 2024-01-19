from django.urls import include, path
from rest_framework import routers

from .views import ClubViewSet, EventViewSet, MyEventListView, SubscriptionViewSet

app_name = "gym_management"

router = routers.DefaultRouter()
router.register(r"events", EventViewSet, basename="events")
router.register(r"clubs", ClubViewSet, basename="clubs")
router.register(r"subscriptions", SubscriptionViewSet, basename="subscriptions")

urlpatterns = [
    path("", include(router.urls)),
    path("myevents/", MyEventListView.as_view(), name="myevent"),
]
