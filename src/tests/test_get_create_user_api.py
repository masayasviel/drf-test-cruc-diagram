from rest_framework.test import APIClient

import pytest


@pytest.mark.django_db
class TestGetCreateUserAPIView:
    def test_get(self):
        from .factories import UserFactory, GroupFactory, GroupUserRelationFactory

        user1 = UserFactory()
        user2 = UserFactory()
        user3 = UserFactory()

        group1 = GroupFactory()
        group2 = GroupFactory()

        GroupUserRelationFactory(user=user1, group=group1)
        GroupUserRelationFactory(user=user2, group=group1)
        GroupUserRelationFactory(user=user2, group=group2)
        GroupUserRelationFactory(user=user3, group=group2)

        res = APIClient().get('/users')
        assert res.status == 200
        assert res.json == []
