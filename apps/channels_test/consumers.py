# coding=utf-8

from django.http import HttpResponse
from channels.handler import AsgiHandler
from channels import Group
from channels.generic.websockets import JsonWebsocketConsumer
from threading import Thread
import time


class BackgroundConsumer(JsonWebsocketConsumer):
    channel_session_user = True
    _threads = {}
    group = None

    def send(self, content, close=False):
        if self.group:
            for name in self.group:
                print "group: send", name, content
                self.group_send(name, content, close=close)
        else:
            super(BackgroundConsumer, self).send(content, close=close)

    def connection_groups(self, **kwargs):
        """
        Called to return the list of groups to automatically add/remove
        this connection to/from.
        """
        if self.group:
            return self.group
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
        if self.__class__._threads.get(channel_name):
            self.__class__._threads[channel_name].append(thread)
        else:
            self.__class__._threads[channel_name] = [thread]

        print "create threads", self.__class__, self.__class__._threads
        thread.start()

    def stop_background(self):
        channel_name = self.message.reply_channel.name
        if channel_name in self.__class__._threads:
            del self.__class__._threads[channel_name]

    def kill_background(self):
        return self.message.reply_channel.name not in self.__class__._threads


class Chat2Consumer(BackgroundConsumer):
    group = ["test.me"]

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



class ChatConsumer(JsonWebsocketConsumer):
    channel_session_user = True
    threads = {}

    def background_thread(self):
        """Example of how to send server generated events to clients."""
        count = 0
        while True:
            channel_name = self.message.reply_channel.name
            if channel_name not in ChatConsumer.threads:
                print channel_name, 'exit'
                return
            count += 1
            print count, ChatConsumer.threads
            self.send({"count": count})
            time.sleep(2)

    def connection_groups(self, **kwargs):
        """
        Called to return the list of groups to automatically add/remove
        this connection to/from.
        """
        return ["test"]

    def connect(self, message, **kwargs):
        """
        Perform things on connection start
        """
        print "connect", self.message.reply_channel.name

        thread = Thread(target=self.background_thread)
        thread.daemon = True


        channel_name = message.reply_channel.name
        if ChatConsumer.threads.get(channel_name):
            ChatConsumer.threads[channel_name].append(thread)
        else:
            ChatConsumer.threads[channel_name] = [thread]

        thread.start()
        print "threads", ChatConsumer.threads

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
        channel_name = message.reply_channel.name
        del ChatConsumer.threads[channel_name]
        pass


def http_consumer(message):
    # Make standard HTTP response - access ASGI path attribute directly
    response = HttpResponse("Hello world! You asked for %s" % message.content['path'])
    # Encode that response into message format (ASGI)
    for chunk in AsgiHandler.encode_response(response):
        message.reply_channel.send(chunk)



# Connected to websocket.connect
def ws_add(message):
    print "ooook"
    Group("chat").add(message.reply_channel)


# Connected to websocket.disconnect
def ws_disconnect(message):
    print "disconnect", message, message.content
    message.reply_channel.send({
        "text": "disconnect",
    })


def ws_message(message):
    # ASGI WebSocket packet-received and send-packet message types
    # both have a "text" key for their textual data.
    print "message", message
    message.reply_channel.send({
        "text": message.content['text'],
    })


def ws_connect(message):
    # ASGI WebSocket packet-received and send-packet message types
    # both have a "text" key for their textual data.
    print "connect", message, message.content
    message.reply_channel.send({
        "text": "connect",
    })