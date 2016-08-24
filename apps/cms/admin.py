from django.contrib import admin
from .models import ConfigModel, HistroyModel
# Register your models here.

admin.site.register(ConfigModel)
admin.site.register(HistroyModel)
