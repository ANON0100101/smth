from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from applications.account.serializers import RegisterSerializer, LoginSerializer, AccountRecoverySerializer, ResetPasswordSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from .utils import send_activation_email
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from applications.account.utils import send_new_password, change_password
from django.core.mail import send_mail
import random
import string

User = get_user_model()


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            surname = serializer.validated_data.get('surname')
            serializer.save(name=name, surname=surname)
            return Response('Вы успешно зарегистрировались. Вам отправлено письмо на почту с активацией', status=201)
        return Response(serializer.errors, status=400)


class ActivationAPIView(APIView):
    def get(self, request, activation_code):
        user = get_object_or_404(User, activation_code=activation_code)
        user.is_active = True
        user.activation_code = ''
        user.save(update_fields=['is_active', 'activation_code'])
        return Response('Успешно', status=200)


class ChangePasswordAPIView(APIView):
    def post(self, request):
        email = request.data.get('email', '')
        current_password = request.data.get('current_password', '')
        new_password = request.data.get('new_password', '')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response('Пользователь с такой почтой не найден', status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(current_password):
            return Response('Неверный текущий пароль', status=status.HTTP_400_BAD_REQUEST)
        if len(new_password) < 6:
            return Response('Новый пароль должен содержать не менее 6 символов', status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        return Response('Пароль успешно изменен', status=status.HTTP_200_OK)

class GenerateAndSendPassword(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Почта не указана.'}, status=status.HTTP_400_BAD_REQUEST)
        new_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь с такой почтой не найден.'}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()
        send_new_password(user, new_password)
        return Response({'message': 'Новый пароль успешно отправлен на ваш email.'}, status=status.HTTP_200_OK)


class ResetPasswordRequestView(APIView):
    def post(self, request):
        email = request.data.get('email', '')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь с такой почтой не найден.'}, status=status.HTTP_404_NOT_FOUND)
        token = str(uuid.uuid4())
        reset_url = reverse('password_reset', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(user.pk)), 'token': token})
        send_reset_password_email(user.email, reset_url)
        return Response({'message': 'Email с инструкциями по сбросу пароля отправлен на вашу почту.'}, status=status.HTTP_200_OK)