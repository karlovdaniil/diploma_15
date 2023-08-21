import factory.django
from factory import Faker

from core.models import User
from goals.models import Board, Goal, GoalCategory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = Faker('name')
    password = Faker('password')


class BoardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Board

    title = Faker('name')


class GoalCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GoalCategory

    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)
    title = Faker('name')


class GoalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Goal

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(GoalCategoryFactory)
    title = Faker('name')
