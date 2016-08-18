# coding=utf-8

from django.http import HttpResponse
from channels.handler import AsgiHandler
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


class Chat2Consumer(BackgroundConsumer):
    rooms = ["test.me"]

    def background(self):
        """Example of how to send server generated events to clients."""
        count = 0
        while True:
            channel_name = self.message.reply_channel.name
            if self.kill_background():
                print channel_name, 'exit'
                return
            count += 1
            print count, self.__class__
            self.send({"count": count})
            time.sleep(2)

    def connect(self, message, **kwargs):
        """
        Perform things on connection start
        """
        print "connect", self.message.reply_channel.name
        self.create_background()

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


class Chat3Consumer(SingleBackgroundConsumer):
    rooms = ["test.me2"]


    def background(self):
        """Example of how to send server generated events to clients."""
        count = 0
        print "background"

        while True:
            print self
            #if self.kill_background():
            #    print self.clients, 'exit'
            #     return
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
