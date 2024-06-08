from django.urls import path

from . import views

urlpatterns = [
    path("", views.NotificationListAPIView.as_view(), name="notification_list"),
    path(
        "mark_as_seen/",
        views.NotificationSeenAPIView.as_view(),
        name="notification_mark_seen",
    ),
    path("check/", views.NotificationCheckAPIView.as_view(), name="notification_check"),
]
