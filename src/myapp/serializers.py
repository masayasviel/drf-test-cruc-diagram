from rest_framework import serializers
from .models import User, Group

class UserListResponseSerializer(serializers.ModelSerializer):
    class GroupSerializer(serializers.ModelSerializer):
        class Meta:
            model = Group
            fields = ('id', 'name')

    groups = serializers.ListField(
        child=GroupSerializer()
    )

    class Meta:
        model = User
        fields = ('id', 'name', 'code', 'groups')
