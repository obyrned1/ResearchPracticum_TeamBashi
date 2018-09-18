from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^trip_info/$', views.trip_info, name='trip_info'),
    url(r'^mapper/$', views.mapper, name='mapper'),
]