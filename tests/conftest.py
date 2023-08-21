from pytest_factoryboy import register

from tests.factories import BoardFactory, GoalCategoryFactory, GoalFactory, UserFactory

pytest_plugins = 'tests.fixtures'
register(UserFactory)
register(BoardFactory)
register(GoalCategoryFactory)
register(GoalFactory)
