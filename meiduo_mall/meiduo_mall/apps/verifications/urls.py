#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.urls import path, re_path
from . import views

urlpatterns = [
    # 请求图形验证码
    path('image_codes/<uuid:uid>/', views.ImageCodeView.as_view(), name='img_code'),
    # 请求短信验证码
    re_path(r'^sms_codes/(?P<phone>1[35896]\d{9})/$', views.SMSCodeView.as_view())
]