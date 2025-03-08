# -*- coding = utf-8 -*-
from django.contrib import admin
from django.urls import path, re_path, include

from . import views

urlpatterns = [
    path('teachers/', views.teachers),
    path('Delete_teachers/<int:id>/', views.Delete_teachers),
    path('Add_teachers/', views.Add_teachers),
    path('teachers/<int:id>/', views.Update_teachers),
]
