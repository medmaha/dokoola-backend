from django.urls import path

from . import views

urlpatterns = [
    path("", views.NotificationListAPIView.as_view(), name="notification_list"),
    path(
        "seen/",
        views.NotificationSeenAPIView.as_view(),
        name="notification_mark_seen",
    ),
    path(
        "reed/",
        views.NotificationReadAPIView.as_view(),
        name="notification_mark_read",
    ),
    path(
        "check/",
        views.NotificationCheckAPIView.as_view(),
        name="notification_check_new",
    ),
]
