# coding=utf-8

from django.http import HttpResponse
from channels import Group
from channels.generic.websockets import JsonWebsocketConsumer
from threading import Thread
import time


class SingleBackgroundConsumer(JsonWebsocketConsumer):
    """
    单一后台进程的
    rooms = 频道房间
    """
    channel_session_user = True
    thread = None
    clients = []
    rooms = None

    def send(self, content, close=False):
        if self.rooms:
            for name in self.rooms:
                print "group: send", name, content
                self.group_send(name, content, close=close)
        else:
            super(SingleBackgroundConsumer, self).send(content, close=close)

    def connection_groups(self, **kwargs):
        """
        Called to return the list of groups to automatically add/remove
        this connection to/from.
        """
        if self.rooms:
            return self.rooms
        return []

    def background(self):
        """
        the function run in background
        """
        pass

    def start_background(self):

        print "start_background", self.__class__.thread

        if not self.__class__.thread or not self.__class__.thread.isAlive():
            thread = Thread(target=self.background)
            thread.daemon = True
            self.__class__.thread = thread
            print "create single threads", self.__class__, self.__class__.thread
            thread.start()

        channel_name = self.message.reply_channel.name
        if channel_name not in self.__class__.clients:
            self.__class__.clients.append(channel_name)
        print 'start', channel_name, self.__class__.clients

    def stop_background(self):
        channel_name = self.message.reply_channel.name
        print "stop", channel_name, self.__class__.clients

        if channel_name in self.__class__.clients:
            self.__class__.clients.remove(channel_name)
        print "after stop", channel_name, self.__class__.clients

    def kill_background(self):
        return not self.__class__.clients


class BackgroundConsumer(JsonWebsocketConsumer):
    """
    rooms = 频道房间
    """
    channel_session_user = True
    threads = {}
    rooms = None

    def send(self, content, close=False):
        if self.rooms:
            for name in self.rooms:
                print "group: send", name, content
                self.group_send(name, content, close=close)
        else:
            super(BackgroundConsumer, self).send(content, close=close)

    def connection_groups(self, **kwargs):
        """
        Called to return the list of groups to automatically add/remove
        this connection to/from.
        """
        if self.rooms:
            return self.rooms
        return []

    def background(self):
        """
        the function run in background
        """
        pass

    def create_background(self):

        thread = Thread(target=self.background)
        thread.daemon = True

        channel_name = self.message.reply_channel.name
        if self.__class__.threads.get(channel_name):
            self.__class__.threads[channel_name].append(thread)
        else:
            self.__class__.threads[channel_name] = [thread]

        print "create threads", self.__class__, self.__class__.threads
        thread.start()

    def stop_background(self):
        channel_name = self.message.reply_channel.name
        if channel_name in self.__class__.threads:
            del self.__class__.threads[channel_name]

    def kill_background(self):
        return self.message.reply_channel.name not in self.__class__.threads

