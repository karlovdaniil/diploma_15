import pytest
from rest_framework import status


@pytest.mark.django_db
def test_login(client, auth_user_response):
    """Test for authorization of a registered user"""
    assert auth_user_response.status_code == status.HTTP_200_OK
