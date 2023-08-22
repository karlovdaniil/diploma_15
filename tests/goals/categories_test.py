import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestGoalCategory:
    url = reverse('goals:create-category')

    def test_create_category_not_auth_ail(self, client, board):
        response = client.post(self.url, data={'title': 'Test_title', 'board': board.title})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('role', [1, 2, 3])
    def test_create_category(self, auth_client, board, board_participant, goal_category, role):
        board_participant.role = role
        board_participant.save()
        response = auth_client.post(self.url, data={'title': goal_category.title, 'board': board.pk})

        if role in (1, 2):
            assert response.status_code == status.HTTP_201_CREATED
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('role', [1, 2, 3])
    def test_delete_goal_category(self, auth_client, board_participant, goal_category, role):
        response = auth_client.delete(f'/goals/goal_category/{goal_category.pk}')
        if board_participant.role in (1, 2):
            assert response.status_code == status.HTTP_204_NO_CONTENT
