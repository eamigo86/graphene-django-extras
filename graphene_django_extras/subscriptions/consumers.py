# -*- coding: utf-8 -*-
from channels.generic.websockets import WebsocketDemultiplexer

__author__ = 'Ernesto'


class GraphqlAPIDemultiplexer(WebsocketDemultiplexer):

    def connect(self, message, **kwargs):
        import json
        """Forward connection to all consumers."""
        resp = json.dumps({
            "channel_id": self.message.reply_channel.name.split('.')[-1],
            "connect": 'success'
        })
        self.message.reply_channel.send({"accept": True, "text": resp})
        for stream, consumer in self.consumers.items():
            kwargs['multiplexer'] = self.multiplexer_class(stream, self.message.reply_channel)
            consumer(message, **kwargs)
