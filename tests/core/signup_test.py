import pytest
from rest_framework import status


@pytest.mark.django_db
def test_signup(client):
    """Test for registering a new user and hashing a password"""
    data = {'id': 6, 'username': 'test_user', 'password': '2nghdk5od', 'password_repeat': '2nghdk5od'}

    expected_response = {'id': 6, 'username': 'test_user', 'first_name': '', 'last_name': '', 'email': ''}

    response = client.post('/core/signup', data, content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == expected_response


@pytest.mark.django_db
def test_signup_not_repeated_password(client):
    """Test for the impossibility of registration if the specified passwords do not match"""
    data = {'username': 'test_user', 'password': '2nghdk5od', 'password_repeat': '1232nghdk5od'}

    response = client.post('/core/signup', data, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
