import pytest
from django.contrib.auth import get_user
from django.urls import reverse
from rest_framework import status

from core.models import User


@pytest.fixture()
def get_url(request) -> None:
    request.cls.url = reverse('core:profile')


@pytest.mark.django_db()
@pytest.mark.usefixtures('get_url')
class TestGetProfileView:
    def test_auth_required(self, client):
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_request_user(self, auth_client):
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self._serialize_response(user=get_user(auth_client))

    @staticmethod
    def _serialize_response(user: User, **kwargs) -> dict:
        data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        data |= kwargs
        return data


@pytest.mark.django_db()
@pytest.mark.usefixtures('get_url')
class TestLogoutView:
    def test_auth_required(self, client):
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_not_deleted_on_logout(self, auth_client, user):
        response = auth_client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert User.objects.filter(id=user.id).exists()

    def test_user_logger_out(self, auth_client):
        response = auth_client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not get_user(auth_client).is_authenticated


@pytest.mark.django_db()
@pytest.mark.usefixtures('get_url')
class TestUpdateProfileView:
    def test_auth_required(self, client):
        response = client.patch(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_username_on_existing(self, auth_client, user_factory):
        another_user = user_factory.create()
        response = auth_client.patch(self.url, data={'username': another_user.username})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'username': ['A user with that username already exists.']}
