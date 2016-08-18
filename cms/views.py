# coding=utf-8
from operator import itemgetter
from django.http import HttpResponseRedirect
from django.views.generic import edit, ListView, TemplateView, DetailView
from django.core.urlresolvers import reverse_lazy
from django.db import models
from django.http import Http404
from .models import ConfigModel, HistroyModel
from .GeneralViews import GeneralModelView, GeneralConfigView
from datetime import datetime
# model 查找
import loader
import json


class CMSIndexView(DetailView, GeneralConfigView):
    template_name = "cms/index.html"

    def get_object(self, queryset=None):
        obj, created = ConfigModel.objects.get_or_create(user=self.request.user)
        return obj

    def get_context_data(self, **kwargs):
        context = super(CMSIndexView, self).get_context_data(**kwargs)
        context['model_list'] = self.get_model_list(self.request.user)
        context['history_list'] = HistroyModel.objects.filter(user=self.request.user).order_by("-action_date")[:10]
        context['now'] = datetime.now()
        return context


class ModelListView(ListView, GeneralModelView, GeneralConfigView):
    template_name = 'cms/model/list.html'
    paginate_by = 20

    def get_filter(self):
        """
        合并search, 和 filter
        """
        res = {}
        _search = self.request.GET.get('search', None)
        _filter = self.request.GET.get('filter', None)
        if _filter or _search:
            if _filter:
                try:
                    k, v = _filter.split(',')
                    res = {k: v}
                except Exception, e:
                    pass
            if _search:
                try:
                    k, v = _search.split(',')
                    res[k+'__icontains'] = v
                except Exception, e:
                    pass
        return res

    def get_group_by_model_class(self):
        """
        获取数据分组
        :return: group_by_model_class or None
        """
        group_by = getattr(self.get_model_admin(self.request.GET['app'], self.request.GET['model']), 'group_by', None)
        if group_by:
            for field in self.model_class._meta.fields:
                if group_by == field.name and type(field) == models.ForeignKey:
                    return field.related_model

        return None

    def get_queryset(self):
        """
        search_by 有search_by时 group_by失效
        filter 优先
        group_by 中度优先
        无 全部
        """
        self.model_class = loader.Loader.get_model_class(self.request.GET['app'], self.request.GET['model'])

        if self.request.GET.get('search_by_group'):
            model_class = self.get_group_by_model_class()
        else:
            model_class = self.model_class

        _filter = self.get_filter()
        if _filter:
            return model_class.objects.filter(**_filter)

        group_by_model_class = self.get_group_by_model_class()
        if group_by_model_class:
            model_class = group_by_model_class

        return model_class.objects.all()

    def get_list_display_verbose(self, app, model_name, list_display):
        """获取list_display 的 verbose_name"""
        res = getattr(self.get_model_admin(app, model_name), 'list_display_verbose_name', {'title': '标题'})
        for field in loader.Loader.get_model_class(app, model_name)._meta.fields:
            if field.name in list_display:
                res[field.name] = field.verbose_name
        return res

    def get_search_fields(self, model_class):
        """
        获取可以查询的数据项
        :return:
        """
        res = []
        for field in model_class._meta.fields:
            if field.name in ['id', 'slug']:
                continue
            res.append((field.name, field.verbose_name))
        return res

    def get_para(self):
        res = {}
        for x in self.request.META['QUERY_STRING'].split('&'):
            name, value = x.split('=')
            res[name] = value
        return res

    def get_url_para(self, para):
        res = ""
        for k,v in para.items():
            if k in ['search_field', 'search_value', 'page']:
                continue
            res += k+"="+v+'&'
        res = res[:-1]
        return res

    def get_context_data(self, **kwargs):
        context = super(ModelListView, self).get_context_data(**kwargs)

        context['para'] = self.get_para()
        context['url_para'] = self.get_url_para(context['para'])
        context['model_verbose'] = self.model_class._meta.verbose_name

        app = context['para']['app']
        model_name = context['para']['model']
        model_class = self.model_class

        group_by = None
        if not self.get_filter() or self.request.GET.get('search_by_group'):
            group_by = getattr(self.get_model_admin(app, model_name), 'group_by', None)

        if group_by:
            context['group_by'] = group_by
            model_class = self.get_group_by_model_class()
            context['list_display'] = ['title']
            context['list_display_verbose_name'] = {'title': u"分组"}
        else:
            context['list_display'] = self.get_list_display(app, model_name, self.request.user)
            context['list_display_verbose_name'] = self.get_list_display_verbose(app, model_name, context['list_display'])

        context['search_fields'] = self.get_search_fields(model_class)

        return context


class ModelCreateView(edit.CreateView, GeneralModelView):
    template_name = 'cms/model/create.html'
    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        para = self.get_request_para(self.request)

        self.object = form.save()
        self.save_action_histroy(user=self.request.user,
                                 app=para['app'],
                                 model_name=para['model'],
                                 model_pk=self.object.pk,
                                 action="create",
                                 snap=str(self.object)
                                 )
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(ModelCreateView, self).get_context_data(**kwargs)
        # 查找时间field项
        #TODO
        context['fields_datetime'] = []
        context['fields_date'] = []
        for field in self.model._meta.fields:
            if self.fields == '__all__' or field.name in self.fields:
                if type(field) == models.DateTimeField:
                    context['fields_datetime'].append(field.name)
                if type(field) == models.DateField:
                    context['fields_date'].append(field.name)

        return context

    def get_success_url(self):
        url = reverse_lazy('cms:model-list')
        return url+'?%s' % self.request.META['QUERY_STRING']

    def get(self, request, *args, **kwargs):
        self.model = loader.Loader.get_model_class(self.request.GET['app'], self.request.GET['model'])
        self.fields = self.get_fields(request)
        return super(ModelCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.model = loader.Loader.get_model_class(self.request.GET['app'], self.request.GET['model'])
        self.fields = self.get_fields(request)
        return super(ModelCreateView, self).post(request, *args, **kwargs)


class ModelDeleteView(edit.DeleteView, GeneralModelView):
    """
    通用删除
    """
    template_name = "cms/model/delete.html"

    def get_queryset(self):
        model = loader.Loader.get_model_class(self.request.GET['app'], self.request.GET['model'])
        return model.objects.all()

    def get_success_url(self):
        para = self.get_request_para(self.request)
        self.save_action_histroy(user=self.request.user,
                                 app=para['app'],
                                 model_name=para['model'],
                                 model_pk=self.object.pk,
                                 action="delete",
                                 snap=str(self.object)
                                 )
        url = reverse_lazy('cms:model-list')
        return url+'?%s' % self.request.META['QUERY_STRING']


class ModelUpdateView(edit.UpdateView, GeneralModelView):
    template_name = 'cms/model/update.html'

    def get_object(self, queryset=None):
        try:
            return super(ModelUpdateView, self).get_object(queryset)
        except Http404:
            self.template_name = "cms/model/model404.html"
        return None

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        para = self.get_request_para(self.request)

        self.object = form.save()
        self.save_action_histroy(user=self.request.user,
                                 app=para['app'],
                                 model_name=para['model'],
                                 model_pk=self.object.pk,
                                 action="update",
                                 snap=str(self.object)
                                 )
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(ModelUpdateView, self).get_context_data(**kwargs)
        context['model'] = self.request.GET['model']
        if not self.object:
            # 对象已删除
            context['model_verbose'] = unicode(getattr(loader.Loader.get_model_class(self.request.GET['app'], self.request.GET['model']), '_meta').verbose_name)
            para = self.get_request_para(self.request)
            res = HistroyModel.objects.filter(app=para['app'], model_name=para['model'],
                                              model_pk=self.kwargs.get('pk'), action="delete")
            if res:
                context['object'] = res[0]

        return context

    def get_success_url(self):
        url = reverse_lazy('cms:model-list')
        return url+'?%s' % self.request.META['QUERY_STRING']

    def get(self, request, *args, **kwargs):
        self.model = loader.Loader.get_model_class(self.request.GET['app'], self.request.GET['model'])
        self.fields = self.get_fields(request)
        return super(ModelUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.model = loader.Loader.get_model_class(self.request.GET['app'], self.request.GET['model'])
        self.fields = self.get_fields(request)
        return super(ModelUpdateView, self).post(request, *args, **kwargs)


class BackupDBView(TemplateView):
    pass


class CmsSettingView(DetailView):
    template_name = "cms/model/setting.html"

    def get_object(self, queryset=None):
        cfg, created = ConfigModel.objects.get_or_create(user=self.request.user)
        return cfg

    def get_context_data(self, **kwargs):
        context = super(CmsSettingView, self).get_context_data(**kwargs)
        context['models'] = {}
        for app, model_name, model_verbose_name in loader.get_models():
            context['models'][model_name] = {'app': app,
                                             'verbose_name': model_verbose_name}
        return context


class CmsSettingModelView(DetailView, GeneralModelView, GeneralConfigView):
    template_name = "cms/model/setting-model.html"


    def get_object(self, queryset=None):
        cfg, created = ConfigModel.objects.get_or_create(user=self.request.user)
        return cfg

    def get_context_data(self, **kwargs):
        context = super(CmsSettingModelView, self).get_context_data(**kwargs)
        app = self.request.GET['app']
        model_name = self.request.GET['model']
        model_class = loader.Loader.get_model_class(app, model_name)
        context['model'] = {'app': self.request.GET['app'],
                            'name': model_name,
                            'verbose_name': model_class._meta.verbose_name,
                            'fields': self.get_model_fields(app, model_name, self.request.user),
                            }
        return context

    def post(self, request, **kwargs):
        self.object = self.get_object()
        cfg = self.get_object().get_config()

        if 'app' not in cfg:
            cfg['app'] = {}

        app = request.POST['app']
        model_name = request.POST['name']

        if app not in cfg['app']:
            cfg['app'][app] = {}

        if model_name not in cfg['app'][app]:
            cfg['app'][app][model_name] = {}

        cfg['app'][app][model_name]['list_display'] = request.POST.getlist('list_display', [])

        self.object.config = json.dumps(cfg)
        self.object.save()
        context = self.get_context_data(object=self.object)
        context['success'] = "True"
        return self.render_to_response(context)

