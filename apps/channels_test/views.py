from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.


class IndexView(TemplateView):
    template_name = "channels_test/index.html"
