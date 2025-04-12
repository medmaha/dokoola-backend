from django.urls import path, re_path

from . import views

urlpatterns = [
    path("create/", views.MessagingCreateAPIView.as_view(), name="m_create"),
    path("threads/", views.ThreadListAPIView.as_view(), name="threads_list"),
    path(
        "threads/delete/",
        views.ThreadDeleteAPIView.as_view(),
        name="m_delete",
    ),
    path("threads/latest/", views.latest_thread, name="thread_latest"),
    path(
        "threads/search/",
        views.ThreadSearchAPIView.as_view(),
        name="m_t_list",
    ),
    path(
        "threads/messages/",
        views.ThreadMessagesAPIView.as_view(),
        name="m_list",
    ),
]
