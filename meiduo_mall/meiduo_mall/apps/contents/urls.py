#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index')
]