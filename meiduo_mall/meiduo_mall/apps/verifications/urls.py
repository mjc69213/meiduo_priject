#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('image_codes/<uuid:uid>/', views.ImageCodeView.as_view(), name='img_code')
]