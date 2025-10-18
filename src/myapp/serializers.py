from rest_framework import serializers
from .models import User, Group

class UserListResponseSerializer(serializers.ModelSerializer):
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ('id', 'name', 'code')

    users = serializers.ListField(
        child=UserSerializer(),
    )

    class Meta:
        model = Group
        fields = ('id', 'name', 'users')


class UserRegisterRequestSerializer(serializers.Serializer):
    name = serializers.CharField()
    code = serializers.CharField()
    group_id = serializers.IntegerField()
