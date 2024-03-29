from django.urls import include, path
from rest_framework import routers

from .views import (CheckEmailVerifyAPIView, CoachListAPIView,
                    ContactEmailView, EmailVerificationUserUpdateView,
                    IndividualEventScheduleListAPIView, PhoneNumberSendSMSView,
                    PhoneNumberVerificationView, ScheduleModelViewSet,
                    TrainerScheduleListAPIView, UserInfoUpdateAPIView,
                    YookassaPaymentView, YookassaWebhookView)

app_name = "users"

router = routers.DefaultRouter()
router.register(r"schedule", ScheduleModelViewSet, basename="schedule")

urlpatterns = [
    path("", include(router.urls)),
    path("user-update/<int:pk>/", UserInfoUpdateAPIView.as_view(), name="user-update"),
    path("coaches/", CoachListAPIView.as_view(), name="coaches-list"),
    path("coaches/<str:time>/", CoachListAPIView.as_view(), name="coaches-list"),
    path(
        "individual_event_schedules/<int:trainer_id>/",
        IndividualEventScheduleListAPIView.as_view(),
        name="individual-event-schedules-list",
    ),
    path(
        "individual_event_schedules/",
        IndividualEventScheduleListAPIView.as_view(),
        name="individual-event-schedules-list",
    ),
    path("schedules/", TrainerScheduleListAPIView.as_view(), name="schedules-list"),
    path("payment/create/", YookassaPaymentView.as_view(), name="payment-create"),
    path("yookassa/webhook/", YookassaWebhookView.as_view(), name="yookassa-webhook"),
    path("verify/phone/", PhoneNumberVerificationView.as_view(), name="phone-verify"),
    path("send/phone/", PhoneNumberSendSMSView.as_view(), name="phone-send"),
    path("contact/", ContactEmailView.as_view(), name="send-email"),
    path(
        "verify/<str:email>/<uuid:code>/",
        EmailVerificationUserUpdateView.as_view(),
        name="email_verify",
    ),
    path(
        "check-email-verify/<int:user_id>/",
        CheckEmailVerifyAPIView.as_view(),
        name="check-email-verify",
    ),
]
