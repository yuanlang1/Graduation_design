"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from . import helloworld
from . import add
from . import server

urlpatterns = [
    path('admin/', admin.site.urls),
    path('helloworld/<int>', helloworld.index),
    path('server/', server.index),
    path('music/', include('music.urls')),
    path('user/', include('user_inf.urls')),
    path('home/', include('home.urls')),
    path('Course_manage/', include('Course_manage.urls')),
    path('Teacher_manage/', include('Teacher_manage.urls')),
    path('Class_manage/', include('Class_manage.urls')),
]
