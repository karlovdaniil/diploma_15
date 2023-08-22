import pytest
from django.urls import reverse
from rest_framework import status

from tests.goals.factories import CreateGoalRequest


@pytest.mark.django_db()
class TestCreateGoalView:
    url = reverse('goals:create-goal')

    def test_create_goal_auth_required_fail(self, client):
        response = client.post(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_goal_not_owner_fail(self, auth_client, goal_category):
        data = CreateGoalRequest.build(category=goal_category.id)
        response = auth_client.post(self.url, data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('role', [1, 2, 3])
    def test_create_goal_owner_or_writer(self, auth_client, board_participant, goal_category, role):
        board_participant.role = role
        board_participant.save(update_fields=['role'])
        data = CreateGoalRequest.build(category=goal_category.id)
        response = auth_client.post(self.url, data=data)
        if role in (1, 2):
            assert response.status_code == status.HTTP_201_CREATED
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_goal_on_deleted_category_fail(self, auth_client, goal_category):
        goal_category.is_deleted = True
        goal_category.save(update_fields=['is_deleted'])
        data = CreateGoalRequest.build(category=goal_category.id)
        response = auth_client.post(self.url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_goal_on_existing_category(self, auth_client):
        data = CreateGoalRequest.build(category=1)
        response = auth_client.post(self.url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
