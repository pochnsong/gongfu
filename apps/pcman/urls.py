# coding=utf-8
from django.conf.urls import url
from views import *

urlpatterns = [
    url(r'^signin/$', SigninView.as_view(), name="signin"),
]