from django.urls import path

from . import views

urlpatterns = [
    path("", views.UserListAPIView.as_view(), name="users"),
    path("websocket", views.get_socket_id, name="users"),
    path("<pk>", views.UserDetailAPIView.as_view(), name="user"),
    path("get-me", views.UserDetailAPIView.as_view(), name="user"),
]
