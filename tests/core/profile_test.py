import pytest
from rest_framework import status
from rest_framework.exceptions import ErrorDetail


@pytest.mark.django_db
def test_get_profile(client, user, auth_user_response):
    """Test for downloading an authorized user profile"""
    expected_response = {'id': user.id, 'username': user.username, 'first_name': '', 'last_name': '', 'email': ''}

    response = client.get('/core/profile')

    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_response


@pytest.mark.django_db
def test_patch_profile(client, user, auth_user_response):
    """Test for changing the data of an authorized user"""
    expected_response = {'id': user.id, 'username': user.username, 'first_name': '123', 'last_name': '123', 'email': ''}

    response = client.patch(
        '/core/profile', data={'first_name': '123', 'last_name': '123'}, content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_response


@pytest.mark.django_db
def test_get_profile_not_authorized(client):
    """Test for closing a profile without authorization"""
    expected_response = {'detail': 'Authentication credentials were not provided.'}
    response = client.get('/core/profile')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data == expected_response


@pytest.mark.django_db
def test_update_password(client, user):
    """Password change test, checking the absence of access using the old password"""
    old_password = user.password
    user.set_password(old_password)
    user.save()
    response = client.post(
        '/core/login', data={'username': user.username, 'password': old_password}, content_type='application/json'
    )

    response = client.patch(
        '/core/update_password',
        data={'old_password': old_password, 'new_password': 'fbvdhvu356'},
        content_type='application/json',
    )

    response_old_password = client.post(
        '/core/login', data={'username': user.username, 'password': old_password}, content_type='application/json'
    )

    response_new_password = client.post(
        '/core/login', data={'username': user.username, 'password': 'fbvdhvu356'}, content_type='application/json'
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response_old_password.status_code == status.HTTP_200_OK
    assert response_new_password.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_passwort_wrong_old_password(client, auth_user_response):
    """Test for the inability to change the password with an incorrect old password"""
    expected_response = {'detail': ErrorDetail(string='Method "PATCH" not allowed.', code='method_not_allowed')}
    response = client.patch(
        '/core/update_password',
        data={'old_password': '123', 'new_password': 'fbvdhvu356'},
        content_type='application/json',
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.data == expected_response
