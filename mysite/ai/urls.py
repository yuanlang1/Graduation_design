# -*- coding = utf-8 -*-
from django.contrib import admin
from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('imgclass/', views.imgclass),
    path('yolo/', views.yolo)
]
