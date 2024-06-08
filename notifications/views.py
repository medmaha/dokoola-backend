from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView, GenericAPIView

from .serializer import NotificationSerializer
from .models import Notification


class NotificationListAPIView(ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self, latest=False):
        user = self.request.user
        if latest:
            queryset = Notification.objects.filter(
                recipient=user, is_seen=False
            ).order_by("-created_at")
        else:
            queryset = Notification.objects.filter(recipient=user).order_by(
                "-created_at"
            )
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset("latest" in request.query_params)  # type: ignore
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        response = self.get_paginated_response(serializer.data)
        return response


class NotificationSeenAPIView(GenericAPIView):

    def post(self, request, *args, **kwargs):
        user = request.user
        notifications = request.data.get("data")
        Notification.objects.select_related().filter(
            recipient=user, id__in=notifications
        ).update(is_seen=True)
        return Response({}, status=200)


class NotificationCheckAPIView(RetrieveAPIView):
    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(recipient=user, is_seen=False)
        return queryset.exists()

    def retrieve(self, request, *args, **kwargs):
        queryset_exists = self.get_queryset()
        return Response({"new": queryset_exists})
