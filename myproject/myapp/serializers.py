from rest_framework import serializers

from .models import Group, Tag, User


class UserListResponseSerializer(serializers.ModelSerializer):
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ("id", "name", "code")

    users = serializers.ListField(
        child=UserSerializer(),
    )

    class Meta:
        model = Group
        fields = ("id", "name", "users")


class UserRegisterRequestSerializer(serializers.Serializer):
    name = serializers.CharField()
    code = serializers.CharField()
    group_id = serializers.IntegerField()


class UserDetailResponseSerializer(serializers.ModelSerializer):
    class GroupSerializer(serializers.ModelSerializer):
        class Meta:
            model = Group
            fields = ("id", "name")

    class TagSerializer(serializers.ModelSerializer):
        class Meta:
            model = Tag
            fields = ("id", "name")

    groups = serializers.ListField(
        child=GroupSerializer(),
    )
    tags = serializers.ListField(
        child=TagSerializer(),
        required=False,
    )

    class Meta:
        model = User
        fields = ("id", "name", "code", "groups", "tags")
