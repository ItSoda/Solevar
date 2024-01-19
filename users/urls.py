from django.urls import include, path
from rest_framework import routers

from .views import CoachViewSet, YookassaPaymentView, YookassaWebhookView

app_name = "users"

router = routers.DefaultRouter()
router.register(r"coaches", CoachViewSet, basename="coaches")

urlpatterns = [
    path("", include(router.urls)),
    path("payment/create/", YookassaPaymentView.as_view(), name="payment-create"),
    path("yookassa/webhook/", YookassaWebhookView.as_view(), name="yookassa-webhook"),
]
