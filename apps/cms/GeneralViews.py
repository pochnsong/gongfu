# coding=utf-8
from operator import itemgetter
import json
from loader import Loader, get_models
from .models import HistroyModel, ConfigModel
__author__ = 'pochnsong@gmail.com'


# 通用后台
class GeneralModelView(object):

    def get_request_para(self, request):
        res = {
            'app': request.GET.get('app', None),
            'model': request.GET.get('model', None),
            }
        return res

    def get_model_admin(self, app, model_name):
        return Loader.get_model_admin(app, model_name)

    def get_fields(self, request):
        _fields = request.GET.get('fields', None)
        _fields = _fields.split(',') if _fields else '__all__'
        return _fields

    def save_action_histroy(self, user, action, app, model_name, model_pk, snap=""):
        """
        保存历史动作
        :return:
        """
        hist = HistroyModel.objects.create(
            user=user,
            app=app,
            action=action,
            model_name=model_name,
            model_pk=model_pk,
            snap=snap
            )
        return hist


# 通用后台
class GeneralConfigView(object):
    """
    _config=ConfigModel.objects.get_or_create(user=cms_user)
    """
    def config(self, cms_user):
        if not hasattr(self, '_config'):
            self._config, created = ConfigModel.objects.get_or_create(user=cms_user)

        return self._config

    def set_dict_value(self, dict_object, key_list, value):
        """
        设置字典的键值
        """
        _current = dict_object
        for _key in key_list[:-1]:

            if _key not in _current:
                _current[_key] = {}
            if not isinstance(_current[_key], dict):
                _current[_key] = {}
            _current = _current[_key]

        _current[key_list[-1]] = value
        return dict_object

    def get_dict_value(self, dict_object, key_list, default=None):
        """

        :param dict_object:
        :param key_list:
        :param default:
        :return:
        """
        _current = dict_object
        res = default
        for _key in key_list:
            if _key in _current:
                _current = _current[_key]
                res = _current
            else:
                return default

        return res

    def get_list_display(self, app, model_name, cms_user):
        """
        获取list_display
        自定义 的 list_display
        admin 的 list_display
        ['title']
        :return: [field-name, ...]
        """
        cfg = self.config(cms_user)
        res = self.get_dict_value(cfg.get_config(), ['app', app, model_name, 'list_display'])

        if res:
            _fields_default = []
            for x in Loader.get_model_class(app, model_name)._meta.fields:
                _fields_default.append(x.name)

            # 不在数据项中的删除
            for x in res:
                if x not in _fields_default:
                    import json
                    res.remove(x)
                    _cfg = self.set_dict_value(cfg.get_config(), ['app', app, model_name, 'list_display'], res)
                    cfg.config = json.dumps(_cfg)
                    cfg.save()

        if not res:
            res = getattr(Loader.get_model_admin(app, model_name), 'list_display', ['title'])

        cfg.update_index_ordering(app, model_name)

        return res

    def get_model_fields(self, app, model_name, cms_user):
        """
        :return: [{'name': 'field_name',
        'verbose_name': 'field_verbose_name',
        'list_display': True or False,
        }, ...]
        """
        # 获取list_display

        list_display = self.get_list_display(app, model_name, cms_user)

        res = []
        for field in Loader.get_model_class(app, model_name)._meta.fields:
            res.append({'name': field.name,
                        'verbose_name': field.verbose_name,
                        'list_display': True if field.name in list_display else False,
                        })
        return res


    def get_model_list(self, user):
        """
        获取首页model排序列表
        :return: [(app, model_name, model_verbose, level), ...]
        """
        cfg = self.config(user).get_config()

        _model_list = self.get_dict_value(cfg, ['index', 'model_list'], default=None)

        if not _model_list:
            _model_list = []
            for app, model_name, model_verbose in get_models():
                _model_list.append((app, model_name, model_verbose, 0))

            self.set_dict_value(cfg, ['index', 'model_list'], _model_list)
            self.config(user).config = json.dumps(cfg)
            self.config(user).save()
        else:
            _model_list_default = get_models()
            changed = False
            for x in list(_model_list):
                # app, model_name, model_verbose, level
                if (x[0], x[1], x[2]) in _model_list_default:
                    _model_list_default.remove((x[0], x[1], x[2]))
                else:
                    print 'remove model_list', x
                    changed = True
                    _model_list.remove(x)

            for app, model_name, model_verbose in _model_list_default:
                print 'add model_list', app, model_name
                changed = True
                _model_list.append([app, model_name, model_verbose, 0])

            if changed:
                cfg = self.set_dict_value(cfg, ['index', 'model_list'], _model_list)
                self.config(user).config = json.dumps(cfg)
                self.config(user).save()

        return sorted(_model_list, key=itemgetter(3), reverse=True)