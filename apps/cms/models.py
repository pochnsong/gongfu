# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
import json
# Create your models here.


class HistroyModel(models.Model):
    user = models.ForeignKey(User)
    action = models.CharField(max_length=32, default="")
    action_date = models.DateTimeField(auto_now_add=True)
    app = models.CharField(max_length=64, default="")
    model_name = models.CharField(max_length=64, default="")
    model_pk = models.IntegerField(default=-1)
    snap = models.CharField(max_length=128, default="", help_text=u"快照")

    def __unicode__(self):
        return self.snap


class ConfigModel(models.Model):
    user = models.OneToOneField(User)
    active = models.BooleanField(verbose_name=u"激活", default=False, blank=True)
    permission = models.TextField(verbose_name=u"权限", default="{}", blank=True)
    config = models.TextField(verbose_name=u"个人配置", default="{}", blank=True)

    def __unicode__(self):
        return str(self.user)

    class Meta:
        verbose_name = u"CMS配置"

    def get_config(self):
        return json.loads(self.config)

    def get_permission(self):
        return json.loads(self.permission)

    def update_index_ordering(self, app, model_name, save=True):
        cfg = self.get_config()
        if 'index' in cfg:
            if 'model_list' in cfg['index']:
                _model_list = []
                for _app, _model_name, model_verbose, level in cfg['index']['model_list']:
                    if app == _app and model_name == _model_name:
                        _model_list.append((_app, _model_name, model_verbose, int(level)+1))
                    else:
                        _model_list.append((_app, _model_name, model_verbose, int(level)))
                cfg['index']['model_list'] = _model_list
        self.config = json.dumps(cfg)
        if save:
            self.save()
