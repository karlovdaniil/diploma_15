import pytest
from rest_framework import status
from rest_framework.exceptions import ErrorDetail

from goals.models import BoardParticipant
from tests.factories import GoalCategoryFactory


@pytest.mark.django_db
def test_create_category(client, auth_user_response, user, goal_category, board):
    """Test for creating a category by a user-participant of the board"""
    fields = ['id', 'created', 'updated', 'title', 'is_deleted', 'board']
    BoardParticipant.objects.create(user=user, board=board)
    response = client.post(
        '/goals/goal_category/create',
        data={'title': goal_category.title, 'board': board.id},
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert list(response.data.keys()) == fields


@pytest.mark.django_db
def test_create_category_not_perm(client, user, board, auth_user_2_response, goal_category):
    """Test for an attempt to create a category by a user who is not a member of the board"""
    BoardParticipant.objects.create(user=user, board=board)

    expected_response = {
        'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')
    }

    create_response = client.post(
        '/goals/goal_category/create',
        data={'title': goal_category.title, 'board': board.id},
        content_type='application/json',
    )

    assert create_response.status_code == status.HTTP_403_FORBIDDEN
    assert create_response.data == expected_response


@pytest.mark.django_db
def test_get_category_list(client, auth_user_response, board, user):
    """Test for getting a list of categories"""
    BoardParticipant.objects.create(user=user, board=board)
    goal_categories = GoalCategoryFactory.create_batch(5, user=user, board=board)
    response = client.get('/goals/goal_category/list')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 5


@pytest.mark.django_db
def test_update_category(client, board, get_category, auth_user_2_response, get_user_2_with_password):
    """A test for updating the board by a participant with the role of Editor"""
    BoardParticipant.objects.create(user=get_user_2_with_password[0], board=board, role=2)
    update_response = client.patch(
        f'/goals/goal_category/{get_category.pk}',
        data={'title': 'updated-category', 'board': board.id},
        content_type='application/json',
    )

    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.data['title'] == 'updated-category'


@pytest.mark.django_db
def test_update_category_no_perm(client, board, get_category, auth_user_2_response, get_user_2_with_password):
    """Test for an attempt to update the board by a participant with the Reader role"""
    BoardParticipant.objects.create(user=get_user_2_with_password[0], board=board, role=3)
    update_response = client.patch(
        f'/goals/goal_category/{get_category.pk}',
        data={'title': 'updated-category', 'board': board.id},
        content_type='application/json',
    )
    expected_response = {'detail': 'You do not have permission to perform this action.'}

    assert update_response.status_code == status.HTTP_403_FORBIDDEN
    assert update_response.data == expected_response
