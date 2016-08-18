# coding=utf-8
from channels.routing import route, route_class
from channels_test.consumers import *

channel_routing = [
    #route("http.request", "channels_test.consumers.http_consumer"),
    route_class(Chat3Consumer, path="^/chat/"),
    #route("websocket.receive", ws_message),
]