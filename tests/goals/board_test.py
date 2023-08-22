import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import Board, BoardParticipant


@pytest.mark.django_db
class TestBoardList:
    url = reverse('goals:boards-list')

    def test_get_board_list_fail(self, client):
        result = client.get(self.url)
        assert result.status_code == status.HTTP_403_FORBIDDEN

    def test_get_board_list(self, auth_client):
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_get_board_list_not_participant(self, auth_client):
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []


@pytest.mark.django_db
class TestBoardCreated:
    url_create = reverse('goals:create-board')

    def test_created_board_not_auth(self, client):
        response = client.post(self.url_create)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_created_board_auth(self, auth_client):
        response = auth_client.post(self.url_create, data={'title': 'Test_Board_created'})
        current_user = response.wsgi_request.user
        created_board = Board.objects.get(pk=response.data['id'])
        owner = BoardParticipant.objects.get(board_id=created_board.pk)

        assert response.status_code == status.HTTP_201_CREATED
        assert current_user == owner.user
