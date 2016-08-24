# coding=utf-8
from django.conf import settings
from django.db.models import Model
import re
__author__ = 'pochnsong@gmail.com'


EXCEPT_APPS = ['django.contrib.admin',
               'django.contrib.auth',
               'django.contrib.contenttypes',
               'django.contrib.sessions',
               'django.contrib.messages',
               'django.contrib.staticfiles',
               'djcelery',
               'ckeditor',
               'ckeditor_uploader',
               'dbport',
               'cms',
               'wa',
               ]


def has_bases(checkclass, baseclass):
    for _baseclass in checkclass.__bases__:
        if _baseclass == baseclass:
            return True
        if _baseclass.__bases__:
            if has_bases(_baseclass, baseclass):
                return True

    return False


def get_models():
    """
    查找当前所有的model
    :return (app名称, model name, model verbose name)
    """
    res = []
    model_list = []
    _in_re = re.compile(r'^__[A-Za-z0-9]+__$')
    for app in settings.INSTALLED_APPS:
        if app in EXCEPT_APPS:
            # 排除
            continue

        pkg = __import__(app, fromlist=['models'])
        if not hasattr(pkg, 'models'):
            continue

        for attrname in dir(pkg.models):

            if _in_re.match(attrname):
                # 排除内部属性__xxxx__
                continue
            try:
                attr = getattr(pkg.models, attrname)
                if has_bases(attr, Model):
                    if hasattr(attr, '_meta'):
                        if not getattr(attr, '_meta').abstract:
                            if attrname in model_list:
                                continue
                            res.append((app, attrname, unicode(getattr(attr, '_meta').verbose_name)))
                            model_list.append(attrname)
                    else:
                        if (app, attrname, attrname) in res:
                            continue
                        res.append((app, attrname, attrname))
            except:
                pass
    return res


def get_model_admin(app, model):
    from django.contrib import admin
    _in_re = re.compile(r'^__[A-Za-z0-9]+__$')
    pkg = __import__(app, fromlist=['admin'])
    if not hasattr(pkg, 'admin'):
        return None

    for attrname in dir(pkg.admin):
        attr = getattr(pkg.admin, attrname)
        if _in_re.match(attrname):
            # 排除内部属性__xxxx__
            continue
        try:
            if has_bases(attr, admin.ModelAdmin):
                if attr.model == model:
                    return attr
        except Exception:
            pass

    return None


class Loader(object):
    _load_model = {}
    _load_model_admin = {}

    @staticmethod
    def get_model_class(app_name, model_name):
        """
        动态载入模型model所在的模块,并返回模型名称
        """
        _model_slug = "%s,%s" % (app_name, model_name)
        if _model_slug not in Loader._load_model:
            print 'new', _model_slug
            pkg = __import__(app_name, fromlist=['models'])
            Loader._load_model[_model_slug] = getattr(pkg.models, model_name)

        return Loader._load_model[_model_slug]

    @staticmethod
    def get_model_admin(app_name, model_name):

        _model_slug = "%s,%s" % (app_name, model_name)
        if _model_slug not in Loader._load_model_admin:
            from django.contrib import admin
            _in_re = re.compile(r'^__[A-Za-z0-9]+__$')
            pkg = __import__(app_name, fromlist=['admin'])
            if not hasattr(pkg, 'admin'):
                Loader._load_model_admin[_model_slug] = None
                return None

            for attrname in dir(pkg.admin):
                attr = getattr(pkg.admin, attrname)
                if _in_re.match(attrname):
                    # 排除内部属性__xxxx__
                    continue
                try:
                    if has_bases(attr, admin.ModelAdmin):
                        if attr.model == model_name:
                            Loader._load_model_admin[_model_slug] = attr
                            return attr
                except Exception, e:
                    pass

        return Loader._load_model_admin.get(_model_slug, None)
