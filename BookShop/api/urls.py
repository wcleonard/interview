from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'post', views.PostViewSet)
router.register(r'comment', views.CommentViewSet)
router.register(r'product', views.ProductViewSet)
router.register(r'profile', views.ProfileViewSet)
router.register(r'category', views.CategoryViewSet)
router.register(r'order', views.OrderViewSet)
router.register(r'orderItem', views.OrderItemViewSet)


app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
