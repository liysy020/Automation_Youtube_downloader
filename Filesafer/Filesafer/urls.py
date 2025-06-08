"""Filestore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, re_path
from django.views.static import serve
from django.conf import settings
from Efile import views as efile
from Login.views import login_request as login, logout_request as logout
from Youtube_downloader.views import download_youtube, serve_download

urlpatterns = [
    re_path (r'^files/(?P<path>.*)$',serve,{'document_root': settings.MEDIA_ROOT}),
    path ('', download_youtube),
    path ('admin/', admin.site.urls),
    path ('login/', login, name = 'login'),
    path ('logout/', logout, name = 'logout'),
    path ('storage/list/', efile.file_list, name = 'file_list'),
    path ('storage/list/<int:pk>', efile.file_list, name = 'file_pk'),
    path ('storage/upload/', efile.file_upload, name = 'file_upload'),
    path ('storage/delete/<int:pk>', efile.file_delete, name = 'file_delete'),
    path ('youtube_downloader/', download_youtube, name = 'youtube_downloader'),
    path ('serve_download/', serve_download, name = 'serve_download'),
]
