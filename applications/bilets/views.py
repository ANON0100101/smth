from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
import uuid
from applications.bilets.serializers import *
from applications.bilets.models import *
from applications.bilets.paginations import *
from applications.bilets.permissions import *
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import logging
import secrets

from applications.bilets.utils import send_order_email


class TicketAPIView(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsOwner]
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
        user = request.user
        like_obj, _ = Like.objects.get_or_create(owner=user, bilet_id=pk)
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
        serializer = RatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rating_obj, _ = Rating.objects.get_or_create(owner=request.user, ticket_id=pk)
        rating_obj.rating = serializer.data['rating']
        rating_obj.save()
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CommentModelViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
