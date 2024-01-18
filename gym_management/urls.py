from django.urls import include, path
from rest_framework import routers
from .views import EventViewSet, MyEventListView, ClubViewSet


app_name = "gym_management"

router = routers.DefaultRouter()
router.register(r"events", EventViewSet, basename="events")
router.register(r"clubs", ClubViewSet, basename="clubs")

urlpatterns = [
    path("", include(router.urls)),
    path("myevents/", MyEventListView.as_view(), name="myevent"),
]