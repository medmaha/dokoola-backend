from django.urls import path

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
    path("auth/", views.UserAuthAPIView.as_view(), name="user_auth"),
    path("<pk>/", views.UserDetailAPIView.as_view(), name="user_details"),
]
