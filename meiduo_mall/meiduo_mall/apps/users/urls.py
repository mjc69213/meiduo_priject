#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.urls import path, re_path
from . import views

urlpatterns = [
    # 请求用户注册页面
    path('register/', views.RegisterView.as_view(), name='register'),
    # 检查用户名是否重复
    re_path(r'^user_repeat/(?P<uname>[a-zA-Z]\w{1,15})/$', views.CheckUserRepeat.as_view()),
    # 检查手机号是否重复
    re_path(r'^phone_repeat/(?P<phone>1[35896]\d{9})/$', views.CheckPhoneRepeat.as_view())
]