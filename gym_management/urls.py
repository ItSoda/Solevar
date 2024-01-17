from django.urls import include, path
from rest_framework import routers
from .views import EventViewSet


app_name = "gym_management"

router = routers.DefaultRouter()
router.register(r"events", EventViewSet, basename="events")

urlpatterns = [
    path("", include(router.urls)),
]