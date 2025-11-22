import uuid

import factory

from myapp import models


class UserFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"user_{n}")
    code = factory.Sequence(lambda _: uuid.uuid4().hex)

    class Meta:
        model = models.User


class GroupFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"group_{n}")
    parent = None

    class Meta:
        model = models.Group


class GroupUserRelationFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)

    class Meta:
        model = models.GroupUserRelation


class TagFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"tag_{n}")

    class Meta:
        model = models.Tag


class UserFollowTagFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    tag = factory.SubFactory(TagFactory)

    class Meta:
        model = models.UserFollowTag
