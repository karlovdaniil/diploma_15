import pytest
from django.contrib.auth import get_user
from django.urls import reverse
from rest_framework import status

from core.models import User
from tests.core.factories import LoginRequest


@pytest.mark.django_db
class TestLoginView:
    url = reverse('core:login')

    def test_user_does_not_exists(self, client):
        data = LoginRequest.create()
        response = client.post(self.url, data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invalid_password(self, client, user):
        data = LoginRequest.create(username=user.username)
        response = client.post(self.url, data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_sessions_creates_on_login(self, client, user_factory):
        data = LoginRequest.create()
        user = user_factory.create(username=data['username'], password=data['password'])
        response = client.post(self.url, data=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self._serialize_response(user)
        assert get_user(client).is_authenticated

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
