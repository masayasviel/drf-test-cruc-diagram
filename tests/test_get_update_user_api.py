import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestGetUpdateUserAPIView:
    def test_get(self):
        from .factories import GroupFactory, GroupUserRelationFactory, UserFactory

        user1 = UserFactory()

        group1 = GroupFactory()
        group2 = GroupFactory()

        GroupUserRelationFactory(user=user1, group=group1)
        GroupUserRelationFactory(user=user1, group=group2)

        res = APIClient().get(f"/users/{user1.code}")
        assert res.status_code == 200
        assert res.json() == {
            "id": user1.id,
            "name": user1.name,
            "code": user1.code,
            "groups": [
                {
                    "id": group1.id,
                    "name": group1.name,
                },
                {
                    "id": group2.id,
                    "name": group2.name,
                },
            ],
        }

    def test_get_with_tag(self):
        from .factories import GroupFactory, GroupUserRelationFactory, TagFactory, UserFactory, UserFollowTagFactory

        user1 = UserFactory()

        group1 = GroupFactory()
        group2 = GroupFactory()

        GroupUserRelationFactory(user=user1, group=group1)
        GroupUserRelationFactory(user=user1, group=group2)

        tag1 = TagFactory()
        tag2 = TagFactory()
        tag3 = TagFactory()

        UserFollowTagFactory(user=user1, tag=tag1)
        UserFollowTagFactory(user=user1, tag=tag2)
        UserFollowTagFactory(user=user1, tag=tag3)

        res = APIClient().get(f"/users/{user1.code}?with_tag=true")
        assert res.status_code == 200
        assert res.json() == {
            "id": user1.id,
            "name": user1.name,
            "code": user1.code,
            "groups": [
                {
                    "id": group1.id,
                    "name": group1.name,
                },
                {
                    "id": group2.id,
                    "name": group2.name,
                },
            ],
            "tags": [
                {
                    "id": tag1.id,
                    "name": tag1.name,
                },
                {
                    "id": tag2.id,
                    "name": tag2.name,
                },
                {
                    "id": tag3.id,
                    "name": tag3.name,
                },
            ],
        }
