from django.contrib.auth.hashers import make_password
from rest_framework import exceptions, serializers

from core.models import User
from todolist.fields import PasswordFields


class CreateUserSerializer(serializers.ModelSerializer):
    password = PasswordFields()
    password_repeat = PasswordFields(validate=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_repeat')

    def validate(self, attrs: dict) -> dict:
        if attrs['password'] != attrs['password_repeat']:
            raise exceptions.ValidationError('Password must match')
        return attrs

    def create(self, validated_data: dict) -> User:
        del validated_data['password_repeat']
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = PasswordFields(validate=False)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class UpdatePasswordSerializer(serializers.Serializer):
    old_password = PasswordFields(validate=False)
    new_password = PasswordFields()

    def validate_old_password(self, old_password: str) -> str:
        request = self.context['request']

        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated

        if not request.user.check_password(old_password):
            raise exceptions.ValidationError('Current password is incorrect')

        return old_password
