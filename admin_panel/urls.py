from django.urls import include, path
from rest_framework import routers
from .views import EventAdminViewSet, TagAdminViewSet, ClubAdminViewSet, IndividualEventAdminViewSet, UserAdminViewSet, SubscriptionAdminViewSet


app_name = "admin_panel"

router = routers.DefaultRouter()
router.register(r"users", UserAdminViewSet, basename="users-admin")
router.register(r"events", EventAdminViewSet, basename="events-admin")
router.register(r"tags", TagAdminViewSet, basename="tags-admin")
router.register(r"clubs", ClubAdminViewSet, basename="clubs-admin")
router.register(r"subscriptions", SubscriptionAdminViewSet, basename="subscriptions-admin")
router.register(
    r"individual_events", IndividualEventAdminViewSet, basename="individual_events-admin"
)

urlpatterns = [
    path("admin/", include(router.urls)),
]