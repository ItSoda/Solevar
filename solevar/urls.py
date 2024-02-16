from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (TokenBlacklistView,
                                            TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)

from solevar.admin import custom_admin_site
from users.views import CustomTokenObtainPairView
from .yasg import urlpatterns as doc_url

urlpatterns = [
    path("admin_panel/", custom_admin_site.urls),
    path("api/", include("users.urls")),
    path("api/", include("gym_management.urls")),
    path("api/", include("chats.urls")),
    # Регистрация, авторизация
    path("auth/", include("djoser.urls")),
    path("api/token/", CustomTokenObtainPairView.as_view(), name="custom-token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
]

urlpatterns += doc_url
