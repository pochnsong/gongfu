# coding=utf-8

from channels import Group
from channels_tool.consumer import BackgroundConsumer, SingleBackgroundConsumer
from channels.generic.websockets import JsonWebsocketConsumer
from threading import Thread
import time


class SpiderQueenConsumer(JsonWebsocketConsumer):
    """
    控制中心
    """
    pass


class SpiderConsumer(JsonWebsocketConsumer):
    clients = {}
    http_user = True

    def connect(self, message, **kwargs):
        """
        Perform things on connection start
        """
        print kwargs, message.user
        print "connect", self.message.reply_channel.name

    def receive(self, content, **kwargs):
        """
        Called when a message is received with either text or bytes
        filled out.
        """
        print content, self.message.reply_channel.name
        self.send(content)

    def disconnect(self, message, **kwargs):
        """
        Perform things on connection close
        """
        pass
