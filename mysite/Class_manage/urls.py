# -*- coding = utf-8 -*-
from django.contrib import admin
from django.urls import path, re_path, include

from . import views

urlpatterns = [
    path('Upload_image/', views.upload_image),
    path('classrooms/', views.classrooms),
    path('Delete_classrooms/<int:id>/', views.Delete_classrooms),
    path('Add_classrooms/', views.Add_classrooms),
    # path('classrooms/<int:id>/', views.Update_classroom),
]

