from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

from applications.account.utils import send_activation_code

# from applications.account.utils import send_activation_code

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

