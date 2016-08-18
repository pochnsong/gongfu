# coding=utf-8
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from views import *

urlpatterns = [
    url(r'^$', login_required(CMSIndexView.as_view()), name="index"),
    url(r'^setting$', login_required(CmsSettingView.as_view()), name="setting"),
    url(r'^setting/model$', login_required(CmsSettingModelView.as_view()), name="setting-model"),
    # 通用后台
    url(r'^model-list/$', login_required(ModelListView.as_view()), name="model-list"),
    url(r'^model-create/$', login_required(ModelCreateView.as_view()), name="model-create"),
    url(r'^model-delete/(?P<pk>[\d]+)/$', login_required(ModelDeleteView.as_view()), name="model-delete"),
    url(r'^model-update/(?P<pk>[\d]+)/$', login_required(ModelUpdateView.as_view()), name="model-update"),
]