from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
import uuid

from django.db.models import Q, Count, Case, When, Value, BooleanField
from rest_framework import viewsets
from applications.bilets.models import Ticket
from .serializers import TicketSerializer
from applications.bilets.serializers import *
from applications.bilets.models import *
from applications.bilets.paginations import *
from applications.bilets.permissions import *
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import logging
import secrets
from django.db.models import Q
from applications.bilets.utils import send_order_email


class TicketAPIView(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['owner', 'title']
    search_fields = ['title']
    ordering_fields = ['id']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        instance.count_views += 1
        instance.save(update_fields=['count_views'])
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def like(self, request, pk, *args, **kwargs):
        permissions_classes = [IsAuthenticated]
        user = request.user
        like_obj, _ = Like.objects.get_or_create(owner=user, ticket_id=pk)
        like_obj.is_like = not like_obj.is_like
        like_obj.save()
        status = 'liked'
        if not like_obj.is_like:
            status = 'unliked'

        return Response({'status': status})

    @action(methods=['POST'], detail=True)
    def favorite(self, request, pk, *args, **kwargs):
        logger = logging.getLogger(__name__)
        user = request.user
        favorite_obj, _ = Favorite.objects.get_or_create(owner=user, ticket_id=pk)
        favorite_obj.is_favorite = not favorite_obj.is_favorite
        favorite_obj.save()
        status = 'favorites'
        if not favorite_obj.is_favorite:
            status = 'not favorite'

        # Добавляем логирование
        logger.info(f"User {user.username} marked ticket {pk} as {status}")

        return Response({'status': status})

    @action(methods=['POST'], detail=True)
    def rating(self, request, pk, *args, **kwargs):
        permission_classes = [CanInteractWithTicket]
        serializer = RatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rating_obj, _ = Rating.objects.get_or_create(owner=request.user, ticket_id=pk)
        rating_obj.rating = serializer.data['rating']
        rating_obj.save()
        return Response(serializer.data)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [CanCreateUpdateDeleteTicket()]
        else:
            return [CanInteractWithTicket()]


    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CommentModelViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        return [CanInteractWithTicket()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Создание заказа без подтверждения

        serializer.save(user=self.request.user)

        return Response('Заказ успешно создан, но требует подтверждения.', status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def confirm_order(self, activation_code):
        order = get_object_or_404(Order, activation_code=activation_code)
        if not order.is_active:
            order.is_active = True
            order.activation_code = ''
            order.save(update_fields=['is_active', 'activation_code'])
            return Response('Заказ успешно подтвержден', status=status.HTTP_200_OK)
        else:
            return Response('Заказ уже был подтвержден', status=status.HTTP_400_BAD_REQUEST)


class OrderActivationAPIView(APIView):
    def get(self, request, activation_code):
        order = get_object_or_404(Order, activation_code=activation_code)

        # Проверьте, что заказ еще не был подтвержден
        if not order.is_active:
            # Подтверждение заказа и установка is_active в True
            order.is_active = True
            order.activation_code = ''
            order.save(update_fields=['is_active', 'activation_code'])

            # Уменьшение total_ticket на 1
            ticket = order.ticket
            if ticket:
                ticket.decrease_total_ticket()

            return Response('Вы успешно подтвердили покупку', status=status.HTTP_200_OK)
        else:
            return Response('Заказ уже был подтвержден', status=status.HTTP_400_BAD_REQUEST)



# class AllCommentsAPIView(viewsets.ReadOnlyModelViewSet):
#     queryset = Comment.objects.all().order_by('-id')
#     serializer_class = CommentSerializer
#     permission_classes = []

# class GetTicketDataAPIView(viewsets.ViewSet):
#         permission_classes = []
#         serializer_class = TicketSerializer
#
#     def retrieve(self, request, *args, **kwargs):
#
#         action_type = kwargs.get('action_type')
#
#         if action_type not in ['like', 'rating', 'favorite', 'comment']:
#             return Response({"detail": "Invalid action type"}, status=status.HTTP_400_BAD_REQUEST)
#
#         user = request.user
#         queryset = Ticket.objects.filter(
#             Q(likes__owner=user, likes__is_like=True) |
#             Q(ratings__owner=user) |
#             Q(comments__owner=user) |
#             Q(favorites__owner=user)
#         ).distinct()
#
#         result = {
#             "action_type": action_type,
#             "data": []
#         }
#
#         for ticket in queryset:
#             data_item = {
#                 "post": ticket.id,
#                 "title": ticket.title,
#                 "comment": "none",
#                 "like": "unliked",
#                 "rating": None,
#                 "favorite": "not favorite"
#             }
#
#             if action_type == 'like':
#                 data_item["like"] = "liked" if ticket.likes.filter(owner=user, is_like=True).exists() else "unliked"
#
#             if action_type == 'rating':
#                 rating_obj = ticket.ratings.filter(owner=user).first()
#                 if rating_obj:
#                     data_item["rating"] = rating_obj.rating
#
#             if action_type == 'favorite':
#                 data_item["favorite"] = "favorite" if ticket.favorites.filter(owner=user, is_favorite=True).exists() else "not favorite"
#
#             if action_type == 'comment':
#                 comment_obj = ticket.comments.filter(owner=user).first()
#                 if comment_obj:
#                     data_item["comment"] = comment_obj.body
#
#             result["data"].append(data_item)
#
#         return Response(result)
#
#
#     def get_permissions(self):
#         if self.action in ['create', 'update', 'partial_update', 'destroy']:
#             return [CanCreateUpdateDeleteTicket()]
#         else:
#             return [CanInteractWithTicket()]
