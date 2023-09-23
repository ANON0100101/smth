from django.urls import path, reverse_lazy
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from applications.account.views import RegisterAPIView, ActivationAPIView, ChangePasswordAPIView, GenerateAndSendPassword

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('activate/<uuid:activation_code>/', ActivationAPIView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('change_password/', ChangePasswordAPIView.as_view()),
    path('generate_and_send_password/', GenerateAndSendPassword.as_view(), name='generate_and_send_password'),
]

