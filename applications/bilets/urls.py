# from rest_framework.urls import path
from applications.bilets.views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('activate/<str:activation_code>/', OrderActivationAPIView, basename='activation_code')
router.register('order', OrderViewSet, basename='order')
router.register('comment', CommentModelViewSet)
router.register('', TicketAPIView)


urlpatterns = []


urlpatterns += router.urls



# from django.urls import path
#
#
# urlpatterns = [
#     path('activate/<uuid:activation_code>/', OrderActivationAPIView.as_view({'get': 'list'})),
#     path('order/', OrderViewSet.as_view({'post': 'list'})),
#     path('comment/', CommentModelViewSet.as_view({'get': 'list'})),
#     path('', TicketAPIView.as_view({'get': 'list'})),
# ]
