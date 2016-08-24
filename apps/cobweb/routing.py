# coding=utf-8
from channels.routing import route, route_class
from .consumers import *

channel_routing = [
    route_class(SpiderConsumer, path="^/spider/"),
]