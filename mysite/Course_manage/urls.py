# -*- coding = utf-8 -*-
from django.contrib import admin
from django.urls import path, re_path, include

from . import views

urlpatterns = [
    # path('Upload_image/', views.upload_image),
    path('courses/', views.courses),
    path('Delete_courses/<int:id>/', views.delete_courses),
    path('Add_courses/', views.add_courses),
    path('courses/<int:id>/', views.update_courses),
]

