from rest_framework.urls import path
from applications.bilets.views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('order', OrderViewSet, basename='order')
router.register('comment', CommentModelViewSet)
router.register('', TicketAPIView)


urlpatterns = []


urlpatterns += router.urls
