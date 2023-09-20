from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrAdminOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.method == 'GET':
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user == obj.owner or request.user.is_staff


class IsOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_authenticated
        return request.user and request.user.is_superuser


class CanCreateUpdateDeleteTicket(permissions.BasePermission):
    def has_permission(self, request, view):
        # Разрешено создавать, удалять и обновлять билеты только администраторам
        return request.user.is_authenticated and request.user.is_staff


class CanInteractWithTicket(permissions.BasePermission):
    def has_permission(self, request, view):
        # Разрешено взаимодействие с билетами (например, комментарии, рейтинги, лайки) аутентифицированным пользователям
        return request.user.is_authenticated