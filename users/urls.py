from django.urls import include, path
from rest_framework import routers

from .views import (
    CoachViewSet,
    ContactEmailView,
    PhoneNumberSendSMSView,
    PhoneNumberVerificationView,
    YookassaPaymentView,
    YookassaWebhookView,
)

app_name = "users"

router = routers.DefaultRouter()
router.register(r"coaches", CoachViewSet, basename="coaches")

urlpatterns = [
    path("", include(router.urls)),
    path("payment/create/", YookassaPaymentView.as_view(), name="payment-create"),
    path("yookassa/webhook/", YookassaWebhookView.as_view(), name="yookassa-webhook"),
    path("verify/phone/", PhoneNumberVerificationView.as_view(), name="phone-verify"),
    path("send/phone/", PhoneNumberSendSMSView.as_view(), name="phone-send"),
    path("contact/", ContactEmailView.as_view(), name="send-email"),
]
