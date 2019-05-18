# 理解解析器parser与渲染器renderer
# from rest_framework import generics
from blog.models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, ProfileSerializer, \
    ProductSerializer, CategorySerializer, OrderSerializer, OrderItemSerializer
# from django.shortcuts import get_object_or_404
# from rest_framework.views import APIView
from rest_framework import viewsets
# from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from shop.models import Profile, Product, Category
from orders.models import Order, OrderItem
from .pagination import MyPagination


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = MyPagination


class CommentViewSet(viewsets.ModelViewSet):
    # 用户和密码存放在HTTP请求头的Authorization头部数据中
    authentication_classes = (BasicAuthentication,)
    # 意味着只有认证用户可以访问该视图
    permission_classes = (IsAuthenticated,)

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = MyPagination


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    pagination_class = MyPagination


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # 局部设置分页
    pagination_class = MyPagination


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = MyPagination


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = MyPagination


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
