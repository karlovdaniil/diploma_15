import pytest
from django.urls import reverse
from rest_framework import status

from core.models import User
from tests.core.factories import SingUpRequest


@pytest.mark.django_db
class TestSignUpView:
    url = reverse('core:signup')

    def test_user_create(self, client):
        data = SingUpRequest.build()
        response = client.post(self.url, data)
        assert response.status_code == status.HTTP_201_CREATED
        user = User.objects.get()
        assert response.json() == self._serialize_response(user)
        assert user.check_password(data['password'])

    def test_password_missmatch(self, client, faker):
        data = SingUpRequest.build(password_repeat=faker.password())
        response = client.post(self.url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'non_field_errors': ['Password must match']}

    def test_user_already_exist(self, client, user):
        data = SingUpRequest.build(username=user.username)
        response = client.post(self.url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'username': ['A user with that username already exists.']}

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
