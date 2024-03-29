from django.urls import path

from . import views

app_name = "chats"


urlpatterns = [
    path("create-room/", views.CreateOrGetRoomAPIView.as_view(), name="create-room"),
    path(
        "chat-admin/room/", views.ChatAdminListAPIView.as_view(), name="chat-admin-room"
    ),
    path(
        "chat-admin/admin/",
        views.FullAdminListAPIView.as_view(),
        name="chat-admin-admin",
    ),
    path("update-room/<str:uuid>/", views.GetRoomAPIView.as_view(), name="update-room"),
]
