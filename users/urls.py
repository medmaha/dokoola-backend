from django.urls import path

from users import auth

from . import views
from .search import UserProfileAPIQueryView

# pattern: /api/users/*/**/
urlpatterns = [
    path("", views.UserListAPIView.as_view(), name="users_list"),
    path(
        "dashboard/",
        views.UserDashboardAPIView.as_view(),
        name="dashboard",
    ),
    path(
        "profile/query/",
        UserProfileAPIQueryView.as_view(),
        name="dashboard",
    ),
    path("auth/", auth.AuthUserAPIView.as_view(), name="auth_user"),
    path("<pk>/", views.UserDetailAPIView.as_view(), name="user_details"),
]
