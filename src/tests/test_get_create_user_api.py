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
        assert res.status_code == 200
        assert res.json() == [
            {
                'id': group1.id,
                'name': group1.name,
                'users': [
                    {
                        'id': user1.id,
                        'name': user1.name,
                        'code': user1.code,
                    },
                    {
                        'id': user2.id,
                        'name': user2.name,
                        'code': user2.code,
                    }
                ]
            },
            {
                'id': group2.id,
                'name': group2.name,
                'users': [
                    {
                        'id': user2.id,
                        'name': user2.name,
                        'code': user2.code,
                    },
                    {
                        'id': user3.id,
                        'name': user3.name,
                        'code': user3.code,
                    }
                ]
            },
        ]

    def test_post(self):
        from .factories import GroupFactory

        group = GroupFactory()

        res = APIClient().post(
            '/users',
            {
                'name': '名前',
                'code': 'user_code',
                'group_id': group.id
            },
            format='json'
        )
        assert res.status_code == 201
