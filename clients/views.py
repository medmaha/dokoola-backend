from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from .serializer import ClientSerializer
from .models import Client


class ClientListView(ListAPIView):
    serializer_class = ClientSerializer

    def get_queryset(self):
        queryset = Client.objects.all()
        return queryset

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=200)
    
    
class UserAPIView(RetrieveAPIView):
    serializer_class = ClientSerializer
    def get_queryset(self):
        user_id = self.kwargs['pk']
        if not user_id:
            return None
        try:
            queryset = Client.objects.get(pk=user_id)
            return queryset
        except:
            return None

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            serializer = self.get_serializer(self.get_queryset())
            return Response(serializer.data, status=200)
        return Response({"message':'The userID provided, doesn't match our database"}, status=404)
        