from django.db.models import Prefetch
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Group, GroupUserRelation
from .serializers import UserListResponseSerializer


class GetCreateUserAPIView(APIView):
    def get(self, request):
        group_with_users = Group.objects.prefetch_related(
            Prefetch(
                'groupuserrelation_set',
                queryset=GroupUserRelation.objects.select_related('user'),
                to_attr='relations'
            )
        )

        for g in group_with_users:
            g.users = [rel.user for rel in g.relations]

        return Response(
            UserListResponseSerializer(group_with_users, many=True).data,
            status=status.HTTP_200_OK,
        )
