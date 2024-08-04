from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.db.models import Q

from utilities.text import get_url_search_params
from users.models import User
from .models import Thread, Message
from .serializer import (
    ThreadListSerializer,
    MessagingListSerializer,
    messagingCreateSerializer,
)


@api_view(["GET"])
def latest_thread(request):
    user = request.user
    thread = Thread.objects.filter(owner=user).latest()

    serializer = ThreadListSerializer(thread, many=False, context={"request": request})

    return Response(serializer.data, status=200)


class ThreadDeleteAPIView(DestroyAPIView):
    def get_queryset(self, id: str):
        thread = Thread.objects.filter(unique_id=id, owner=self.request.user).first()
        deleted = False

        if thread:
            thread.delete()
            deleted = True

        return deleted

    def destroy(self, request, *args, **kwargs):
        id = request.data.get("id")

        if not id:
            return Response(
                {"message": "This request is forbidden/prohibited"}, status=403
            )

        if self.get_queryset(id):
            return Response({}, status=200)
        return Response({"message": "This request is forbidden/prohibited"}, status=403)


class ThreadListAPIView(ListAPIView):
    serializer_class = ThreadListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Thread.objects.filter(owner=user, messaging__gt=0).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        response = self.get_paginated_response(serializer.data)
        return response


class ThreadSearchAPIView(ListAPIView):
    serializer_class = ThreadListSerializer

    def get_queryset(self):
        search_params = get_url_search_params(self.request.get_full_path())
        user = self.request.user
        query = search_params.get("q")

        if query:
            queryset = Thread.objects.filter(
                Q(recipient__username__icontains=query)
                | Q(recipient__first_name__icontains=query)
                | Q(recipient__last_name__icontains=query),
                owner=user,
            )
            return queryset

        return []

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        response = self.get_paginated_response(serializer.data)
        return response


class ThreadMessagesAPIView(ListAPIView):
    serializer_class = MessagingListSerializer

    def get_queryset(self, query_params):
        user = self.request.user
        thread_unique_id = query_params.get("id", "")

        print(thread_unique_id)
        if isinstance(thread_unique_id, list):
            thread_unique_id = thread_unique_id[0]
        print(thread_unique_id)

        thread = Thread.objects.filter(owner=user, unique_id=thread_unique_id).first()

        if thread:
            queryset = thread.messaging.all().order_by("-created_at")
            return queryset
        return

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset(request.query_params)

        if not queryset:
            return Response(status=403)

        ps = self.pagination_class.page_size = 15  # type: ignore

        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)  # type:ignore


class messagingCreateAPIView(CreateAPIView):
    serializer_class = messagingCreateSerializer

    def create(self, request, *args, **kwargs):
        recipient_username = request.data.get("recipient")
        recipient = User.objects.filter(username=recipient_username).first()

        invalid_msg = "This request is invalid"

        if not recipient:
            return Response({"message": invalid_msg}, status=400)

        user = request.user

        user_thread, created = Thread.objects.get_or_create(
            owner=user, recipient=recipient
        )
        recipient_thread = Thread.objects.get_or_create(
            owner=recipient, recipient=user
        )[0]

        unique_id = user.username + "__" + recipient.username

        if not user_thread.unique_id:
            user_thread.unique_id = unique_id
            user_thread.save()
        if not recipient_thread.unique_id:
            recipient_thread.unique_id = unique_id
            recipient_thread.save()

        message_data = {}
        message_data["sender"] = user
        message_data["recipient"] = recipient
        message_data["content"] = request.data.get("content")

        serializer = self.get_serializer(
            data=message_data, context={"request": request}
        )

        if serializer.is_valid():
            message = Message.objects.create(**message_data)

            user_thread.messaging.add(message)
            recipient_thread.messaging.add(message)

            serializer = MessagingListSerializer(message, context={"request": request})

            response = {"chat": serializer.data}

            if created:
                t_serializer = ThreadListSerializer(
                    user_thread, context={"request": request}
                )
                response["thread"] = t_serializer.data

            return Response(response, status=201)

        return Response({"message": invalid_msg}, status=400)
