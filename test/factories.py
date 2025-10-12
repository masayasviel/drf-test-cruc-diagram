import uuid

import factory

from src.myapp import models


class UserFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"user_{n}")
    code = factory.Sequence(lambda _: uuid.uuid4().hex)

    class Meta:
        model = models.User


class GroupFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"group_{n}")
    code = factory.Sequence(lambda _: uuid.uuid4().hex)
    parent = None

    class Meta:
        model = models.Group


class GroupUserRelationFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)

    class Meta:
        model = models.GroupUserRelation
