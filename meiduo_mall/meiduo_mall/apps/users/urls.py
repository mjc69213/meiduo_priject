#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.urls import path, re_path
from . import views

urlpatterns = [
    # 请求用户注册页面
    path('register/', views.RegisterView.as_view(), name='register')
]