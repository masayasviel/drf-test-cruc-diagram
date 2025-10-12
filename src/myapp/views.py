from django.db.models import Prefetch
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import User, Group
from .serializers import UserListResponseSerializer


class GetCreateUserAPIView(APIView):
    def get(self, request):
        users = User.objects.prefetch_related(
            Prefetch(
                'groupuserrelation__group',
                queryset=Group.objects.all(),
                to_attr='groups'
            )
        )
        return Response(
            UserListResponseSerializer(users, many=True).data,
            status=status.HTTP_200_OK,
        )
