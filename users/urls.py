from django.urls import include, path
from rest_framework import routers
from .views import CoachViewSet


app_name = "users"

router = routers.DefaultRouter()
router.register(r"coaches", CoachViewSet, basename="coaches")

urlpatterns = [
    path("", include(router.urls)),
]