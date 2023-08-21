from rest_framework import exceptions, serializers

from bot.models import TgUser


class TgUserSerializer(serializers.ModelSerializer):
    tg_id = serializers.IntegerField(source='telegram_chat_id', read_only=True)
    username = serializers.CharField(allow_null=True, read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    verification_code = serializers.CharField(write_only=True)

    class Meta:
        model = TgUser
        fields = ('tg_id', 'username', 'user_id', 'verification_code')

    def validate_verification_code(self, code: str) -> str:
        try:
            self.instance = TgUser.objects.get(verification_code=code)
        except TgUser.DoesNotExist:
            raise exceptions.ValidationError('Неправильный код верификации')
        return code
