# -*- coding = utf-8 -*-
from django.contrib import admin
from django.urls import path, re_path, include

from . import views

urlpatterns = [
    # path('information/', views.information)
    path('top_stats/', views.top_stats),
    path('chart_data/', views.chart_data),
    path('top10_classes/', views.top10_classes)
]
