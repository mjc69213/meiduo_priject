#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.urls import path, re_path
from . import views

urlpatterns = [
    # 请求用户注册页面
    path('register/', views.RegisterView.as_view(), name='register'),
    re_path(r'^user_repeat/(?P<uname>[a-zA-Z]\w{1,15})/$', views.CheckUserRepeat.as_view())
]