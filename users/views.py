from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializer import UserSerializer
from .models import User
from utilities.text import get_url_search_params

from django.db.models import Q


@api_view(["GET", "POST"])
def get_socket_id(request):
    user: User = request.user

    if request.method == "POST":
        socket = request.data.get("socket")

        if socket:
            user.websocket_id = socket
            user.save()

    return Response({"socket": user.websocket_id})


class UserListAPIView(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        url = self.request.get_full_path()
        query = get_url_search_params(url).get("q")

        if query:
            queryset = User.objects.filter(
                Q(username__startswith=query)
                | Q(first_name__startswith=query)
                | Q(last_name__startswith=query)
            )
            return queryset

        queryset = User.objects.filter(is_active=True)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(serializer.data)


class UserDetailAPIView(RetrieveAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            serializer = self.get_serializer(self.get_queryset())
            return Response(serializer.data, status=200)
        return Response({}, status=404)


class UserDashboardAPIView(RetrieveAPIView):

    def retrieve(self, request, *args, **kwargs):
        user: User = request.user
        profile, profile_name = user.profile
        data = {}
        status = 200

        if profile_name == "Freelancer":
            data["projects_count"] = 1
            status = 200

        if profile_name == "Client":
            data["projects_count"] = profile.jobs.count()
            status = 200

        return Response(data, status=status)
