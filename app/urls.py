from django.urls import path

from app import views

urlpatterns = [
    path('', views.index),  # 首页
    path('login/', views.login),  # 登录
    path('register/', views.register),  # 注册
    path('active/', views.active),  # 激活
    path('logout/', views.logout),  # 退出登录

    path('add_addr_book/', views.add_addr_book),  # 增加
    path('search/', views.search),  # 查找
    path('del_addr_book/', views.del_addr_book),  # 删除
    path('update_addr_book/', views.update_addr_book),  # 修改

    path('upload_avatar/', views.upload_avatar),  # 上传头像

    path('api/line/', views.line),  # 获取统计数据

    path('api/verify_code_img/', views.verify_code_img),  # 验证码
]
