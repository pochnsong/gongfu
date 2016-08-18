# coding=utf-8
from django import template
from datetime import datetime

register = template.Library()

@register.filter(name='get')
def get_value(value, key):

    if isinstance(value, dict):
        if key in value:
            return value[key]

    res = getattr(value, key, value)

    if callable(res):
        res = res()

    return res


@register.filter(name='fmt')
def format_value(value):
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')

    if isinstance(value, bool):
        return u"是" if value else u"否"

    if value is None:
        return u"无"

    if value == "":
        return u"无"

    return value


@register.filter(name='zh')
def zh_value(value):
    if value == "update":
        return u"更新"
    if value == "create":
        return u"新建"
    if value == "delete":
        return u"删除"

    return value


@register.filter(name="is_date")
def check_field_is_date(value):
    from django.forms.fields import DateField
    if isinstance(value.field, DateField):
        return True

    return False


@register.filter(name="is_datetime")
def check_field_is_datetime(value):
    from django.forms.fields import DateTimeField
    if isinstance(value.field, DateTimeField):
        return True

    return False


@register.filter(name="date_value")
def check_field_is_date(value):
    if not value:
        return ""
    return value.strftime('%Y-%m-%d')


@register.filter(name="model_label")
def get_model_label(model_name, model_list):
    """
    找到model_list中对应model_name的model_verbose
    :param value:
    :param model_list: (app_name, model_name, model_verbose)
    :return:
    """
    for x in model_list:
        if x[1] == model_name:
            return x[2]

    return model_name


@register.filter(name="datetime_now")
def datetime_now(value):
    """
    找到model_list中对应model_name的model_verbose
    :param value:
    :param model_list: (app_name, model_name, model_verbose)
    :return:
    """
    if not value:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return value.strftime('%Y-%m-%d %H:%M:%S')


@register.filter(name="datetime_value")
def datetime_value(value):
    if not value:
        return ""
    return value.strftime('%Y-%m-%d %H:%M:%S')

@register.filter(name="set_count")
def get_set_count(obj, fk):
    """
    """
    fk_set = (fk+"_set").lower()
    print obj, fk_set
    return getattr(obj, fk_set).count()
