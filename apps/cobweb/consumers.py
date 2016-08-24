# coding=utf-8

from django.http import HttpResponse
from channels.handler import AsgiHandler
from channels import Group
from channels_tool.consumer import BackgroundConsumer, SingleBackgroundConsumer
from channels.generic.websockets import JsonWebsocketConsumer
from threading import Thread
import time


class SpiderConsumer(SingleBackgroundConsumer):

    def connection_groups(self, **kwargs):
        """
        Called to return the list of groups to automatically add/remove
        this connection to/from.
        """
        print 'kwarg',kwargs
        return ["test"]


    def background(self):
        """Example of how to send server generated events to clients."""
        count = 0
        print "background"

        while True:
            print self
            count += 1
            print count, self.__class__.clients
            self.send({"count": count})
            time.sleep(2)

    def connect(self, message, **kwargs):
        """
        Perform things on connection start
        """
        print "connect", self.message.reply_channel.name
        self.start_background()

    def receive(self, content, **kwargs):
        """
        Called when a message is received with either text or bytes
        filled out.
        """
        self.send(content)

    def disconnect(self, message, **kwargs):
        """
        Perform things on connection close
        """
        self.stop_background()
        pass
