from rest_framework.urls import path
from applications.bilets.views import *
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register('order', OrderViewSet, basename='order')
router.register('comment', CommentModelViewSet)
router.register('', TicketAPIView)


urlpatterns = [
    path('activate/<uuid:activation_code>', OrderActivationAPIView.as_view()),
    path('usd_rate/', views.get_usd_rate, name='usd_rate'),
    path('update_usd_rate/', views.update_usd_rate, name='update_usd_rate'),

    # path('bilets/get_data/<str:action_type>/', GetTicketDataAPIView.as_view({'get': 'list'}), name='get-ticket-data'),
]


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
