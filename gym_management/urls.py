from django.urls import include, path
from rest_framework import routers
from .views import EventViewSet, MyEventListView


app_name = "gym_management"

router = routers.DefaultRouter()
router.register(r"events", EventViewSet, basename="events")

urlpatterns = [
    path("", include(router.urls)),
    path("myevents/", MyEventListView.as_view(), name="myevent"),
]