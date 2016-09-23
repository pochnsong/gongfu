# coding=utf-8
from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.

class ResetPCPasswordView(TemplateView):
    template_name = "pcman/reset-pc-password.html"

