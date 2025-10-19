import unicodedata

from django.db import transaction
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Group, GroupUserRelation, User, UserFollowTag
from .serializers import UserDetailResponseSerializer, UserListResponseSerializer, UserRegisterRequestSerializer


class GetCreateUserAPIView(APIView):
    def get(self, request):
        group_with_users = Group.objects.prefetch_related(
            Prefetch(
                "groupuserrelation_set",
                queryset=GroupUserRelation.objects.select_related("user"),
                to_attr="group_user_relation",
            )
        )

        for g in group_with_users:
            g.users = [rel.user for rel in g.group_user_relation]

        return Response(
            UserListResponseSerializer(group_with_users, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = UserRegisterRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        if User.objects.filter(code=data["code"]).first():
            return Response(status=status.HTTP_409_CONFLICT)

        group = Group.objects.filter(id=data["group_id"]).first()
        if not group:
            return Response(status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            user = User.objects.create(name=data["name"], code=data["code"])

            GroupUserRelation.objects.create(
                user=user,
                group=group,
            )

        return Response(status=status.HTTP_201_CREATED)


class GetUpdateUserAPIView(APIView):
    def get(self, request, user_code: str):
        with_tag = unicodedata.normalize(
            "NFKC",
            request.query_params.get("with_tag", "false").lower(),
        ) in ("true", "y", "yes", "1")

        qs = User.objects.prefetch_related(
            Prefetch(
                "groupuserrelation_set",
                queryset=GroupUserRelation.objects.select_related("group"),
                to_attr="group_user_relation",
            )
        )

        if with_tag:
            qs = qs.prefetch_related(
                Prefetch(
                    "userfollowtag_set",
                    queryset=UserFollowTag.objects.select_related("tag"),
                    to_attr="user_follow_tag",
                )
            )

        user = qs.filter(code=user_code).first()

        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user.groups = [rel.group for rel in user.group_user_relation]

        if with_tag:
            user.tags = [rel.tag for rel in user.user_follow_tag]

        return Response(
            UserDetailResponseSerializer(user).data,
            status=status.HTTP_200_OK,
        )
