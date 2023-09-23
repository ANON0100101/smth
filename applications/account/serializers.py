from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

from applications.account.utils import send_activation_code

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(required=True, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ('name', 'surname', 'phone_number', 'email', 'password', 'password2')

    def validate_email(self, email):
        return email

    def validate(self, attrs):
        p1 = attrs.get('password')
        p2 = attrs.pop('password2')

        if p1 != p2:
            raise serializers.ValidationError('Пароли не совпадают!')
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        send_activation_code(user.email, user.activation_code)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            return email
        raise serializers.ValidationError('Нет такого пользователя!')

    def validate(self, attrs):
        user = authenticate(username=attrs.get('email'), password=attrs.get('password'))  # user or None
        if user:
            attrs['user'] = user
            return attrs
        raise serializers.ValidationError('Неверный пароль!')


class CreatePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, min_length=6, write_only=True)
    current_password = serializers.CharField(required=True, write_only=True)

    class Meta:
        models = User
        fields = ('email', 'password', 'new_password', 'current_password')


class AccountRecoverySerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()  # Добавляем поле для токена

    def validate(self, data):
        email = data.get('email')
        token = data.get('token')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Пользователь с таким email не существует')

        # Декодируем uidb64 и проверяем токен
        try:
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            if not default_token_generator.check_token(user, token):
                raise serializers.ValidationError('Недействительный токен')
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError('Недопустимые параметры uidb64 или пользователь не найден')

        # Возвращаем проверенные данные
        return data



class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()