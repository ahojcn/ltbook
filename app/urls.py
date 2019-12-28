from django.urls import path

from app import views

urlpatterns = [
    path('', views.index),  # 首页
    path('login/', views.login),  # 登录
    path('register/', views.register),  # 注册
    path('active/', views.active),  # 激活

    path('api/verify_code_img/', views.verify_code_img),  # 验证码
]
