from django.urls import path

from . import views

urlpatterns = [
    path("", views.UserListAPIView.as_view(), name="users_list"),
    path("websocket", views.get_socket_id, name="users_websocket"),
    path("dashboard/", views.UserDashboardAPIView.as_view(), name="dashboard"),
    path("<pk>/", views.UserDetailAPIView.as_view(), name="user_details"),
    path("get-me/", views.UserDetailAPIView.as_view(), name="user_get_me"),
]
