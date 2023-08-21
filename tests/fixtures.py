import pytest

from goals.models import BoardParticipant
from tests.factories import GoalCategoryFactory, UserFactory


@pytest.mark.django_db
@pytest.fixture
def auth_user_response(user, client):
    """A fixture with the authorization of a registered user"""
    password = user.password
    user.set_password(user.password)
    user.save()
    response = client.post(
        '/core/login', data={'username': user.username, 'password': password}, content_type='application/json'
    )

    return response


@pytest.mark.django_db
@pytest.fixture
def get_user_2_with_password():
    """A fixture with a second user to check access.
    Returns a tuple of the user and his password in an unhashed form"""
    user_2 = UserFactory(username='user2', password='fndkivhtb13')
    password = user_2.password
    user_2.set_password(user_2.password)
    user_2.save()
    return user_2, password


@pytest.mark.django_db
@pytest.fixture
def auth_user_2_response(get_user_2_with_password, client):
    """Fixture with authorization of the second user"""
    response = client.post(
        '/core/login',
        data={'username': get_user_2_with_password[0].username, 'password': get_user_2_with_password[1]},
        content_type='application/json',
    )

    return response


@pytest.mark.django_db
@pytest.fixture
def get_category(board, user):
    """A fixture with a category related to a board with a created user participant
    Returns the category"""
    BoardParticipant.objects.create(user=user, board=board)
    goal_category = GoalCategoryFactory.create(user=user, board=board)
    return goal_category
