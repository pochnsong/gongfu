# coding=utf-8
import os
from channels.asgi import get_channel_layer

os.environ["DJANGO_SETTINGS_MODULE"] = "gongfu.settings"

channel_layer = get_channel_layer()
