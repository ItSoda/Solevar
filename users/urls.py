from django.urls import include, path
from rest_framework import routers

from .views import (CoachListAPIView, ContactEmailView, PhoneNumberSendSMSView,
                    PhoneNumberVerificationView, ScheduleListAPIView,
                    ScheduleModelViewSet, UserInfoUpdateAPIView,
                    YookassaPaymentView, YookassaWebhookView)

app_name = "users"

router = routers.DefaultRouter()
router.register(r"schedule", ScheduleModelViewSet, basename="schedule")

urlpatterns = [
    path("", include(router.urls)),
    path("user-update/<int:pk>/", UserInfoUpdateAPIView.as_view(), name="user-update"),
    path("coaches/", CoachListAPIView.as_view(), name="coaches-list"),
    path("coaches/<str:time>/", CoachListAPIView.as_view(), name="coaches-list"),
    path("schedules/", ScheduleListAPIView.as_view(), name="schedules-list"),
    path(
        "schedules/<int:trainer_id>/",
        ScheduleListAPIView.as_view(),
        name="schedules-list-trainer",
    ),
    path("payment/create/", YookassaPaymentView.as_view(), name="payment-create"),
    path("yookassa/webhook/", YookassaWebhookView.as_view(), name="yookassa-webhook"),
    path("verify/phone/", PhoneNumberVerificationView.as_view(), name="phone-verify"),
    path("send/phone/", PhoneNumberSendSMSView.as_view(), name="phone-send"),
    path("contact/", ContactEmailView.as_view(), name="send-email"),
]
