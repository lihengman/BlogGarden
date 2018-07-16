"""BlogGarden URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path,re_path
from blog import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('cnblogs.com/', views.index),
    path('logout/', views.logout),
    path('', views.index),
    path('digg/', views.digg),
    path('comment/',views.comment),

    path('backend/',views.backend),
    re_path('backend/add_article/',views.add_article),

    path('upload/',views.upload),

    re_path('backend/edit_article/(\d+)/$', views.edit_article),
    re_path('backend/del_article/(\d+)/$', views.del_article),

    re_path('(?P<username>\w+)/articles/(?P<article_id>\d+)$', views.article_detail),

    re_path('(?P<username>\w+)/(?P<condition>category|tag|achrive)/(?P<params>.*)', views.homesite),

    re_path('(?P<username>\w+)/$',views.homesite),

]
