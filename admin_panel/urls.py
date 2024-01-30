from django.urls import include, path
from rest_framework import routers

from .views import (EventAdminViewSet, IndividualEventAdminViewSet,
                    SubscriptionAdminViewSet, UserAdminViewSet)

app_name = "admin_panel"

router = routers.DefaultRouter()
router.register(r"users", UserAdminViewSet, basename="users-admin")
router.register(r"events", EventAdminViewSet, basename="events-admin")
router.register(
    r"subscriptions", SubscriptionAdminViewSet, basename="subscriptions-admin"
)
router.register(
    r"individual_events",
    IndividualEventAdminViewSet,
    basename="individual_events-admin",
)

urlpatterns = [
    path("admin/", include(router.urls)),
]
