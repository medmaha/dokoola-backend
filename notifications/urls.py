from django.urls import re_path

from . import views

urlpatterns = [
    re_path("", views.NotificationListAPIView.as_view(), name="notification_list"),
    re_path(
        "check", views.NotificationCheckAPIView.as_view(), name="notification_check"
    ),
]
