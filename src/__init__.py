import websocket
import thread
import json
import sys
import logging

class Client(object):

    def __init__(self, url, **handlers):
        self.logger = logging.getLogger("webrocket.Client")
        self.logger.addHandler(logging.StreamHandler())
        self.url = url
        self.handlers = handlers
        self.ws = websocket.WebSocket()

    def connect(self, **options):
        try:
            self.ws.connect(self.url, **options)
            self.logger.debug("Connected to %s", self.url)
            return True
        except websocket.WebSocketException as err:
            self.logger.error("Couldn't connect with %s: %s", self.url, err)
            return False
            
    def authenticate(self, access, secret):
        if not self.__check_connection():
            return
        
        payload = {'auth': {'access': access, 'secret': secret}}
        answer = self.send_and_read(payload)

        if not answer.is_error():
            self.logger.debug("Authenticated with %s access", access)
            return True
        else:
            self.logger.error("Authentication failed: %s", answer['err'])
            return False
        
    def subscribe(self, channel):
        if not self.__check_connection():
            return
        
        payload = {'subscribe': {'channel': channel}}
        answer = self.send_and_read(payload)

        if not answer.is_error():
            self.logger.debug("Subscribed to `%s` channel", channel)
            return Channel(self, channel)
        else:
            self.logger.error("Subscription to `%s` failed: %s\n", channel, answer['err'])
            return None

    def publish(self, event):
        if not self.__check_connection():
            return
    
        payload = event.serialize()
        self.ws.send(payload)
        answer = self.read()

        if not answer.is_error():
            self.logger.debug("Event published: %s", event)
            return True
        else:
            self.logger.error("Couldn't publish event: %s\n", answer['err'])
            return None
            
    def logout(self):
        if not self.__check_connection():
            return
        
        payload = {'logout': True}
        answer = self.send_and_read(payload)
        
        if not answer.is_error():
            self.logger.debug("Logged out")
            return True
        else:
            self.logger.error("Coudn't log out: ", answer['err'])
            return False
            
    def disconnect(self):
        if not self.__check_connection():
            return
        
        self.ws.close()
        self.logger.debug("Disconnected")
        return True
        
    def send(self, payload):
        if self.ws.connected:
            return self.ws.send(json.dumps(payload))

    def read(self):
        if self.ws.connected:
            answer = self.ws.recv()
            return Answer(json.loads(answer))

    def send_and_read(self, payload):
        self.send(payload)
        return self.read()

    def __check_connection(self):
        if not self.ws.connected:
            self.logger.error("Not connected!")
            return False
        else:
            return True
    
class Answer(dict):
    
    def is_ok(self):
        return 'ok' in self and self['ok']

    def is_error(self):
        return 'err' in self
    
class Channel(object):

    def __init__(self, client, name):
        self.__client = client
        self.name = name

    def unsubscribe(self):
        pass

    def publish(self, event_name, **data):
        event = Event(self, event_name, **data)
        return self.__client.publish(event)

class Event(object):

    def __init__(self, channel, event, **data):
        self.channel = channel
        self.event = event
        self.data = data

    def serialize(self):
        return json.dumps({'publish': {
            'channel': self.channel.name,
            'event': self.event,
            'data': self.data}})

    def __repr__(self):
        return "<Event(%s): channel=%s, data=%s>" % (
            self.event, self.channel.name, self.data)
    
if __name__ == "__main__":
    c = Client("ws://localhost:9772/echo")
    c.logger.setLevel(logging.DEBUG)
    c.connect()
    c.authenticate("read-write", "secret")
    hello = c.subscribe("hello")
    hello.publish('foo', **{'raz': 'dwa'})
    
class InvalidCredentialsError(Exception):
    pass

class AccessDeniedError(Exception):
    pass

class InvalidChannelNameError(Exception):
    pass

class InvalidChannelError(Exception):
    pass

class InvalidDataError(Exception):
    pass
