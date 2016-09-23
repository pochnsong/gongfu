# coding=utf-8
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class PcmanModel(models.Model):
    name= models.CharField(max_length=30, verbose_name=u"名陈", blank=True, null=True)

    class Meta:
        verbose_name = "系统"