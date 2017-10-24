# -*- coding: utf-8 -*-
import json
from channels import Group
from channels_api import detail_action
from rest_framework.exceptions import ValidationError

__author__ = 'Ernesto'


class UnsubscribeMixin(object):

    @detail_action()
    def unsubscribe(self, pk, data, **kwargs):
        if 'action' not in data:
            raise ValidationError('action required')
        action = data['action']
        group_name = self._group_name(action, id=pk)
        Group(group_name).discard(self.message.reply_channel)
        return {'action': action}, 200


class DjangoGraphqlBindingMixin(object):

    def deserialize(self, message):
        body = json.loads(message['text'])
        self.request_id = body.get("request_id")
        action = body.get('action')
        data = body.get('data', None)
        pk = data.get('id', None)
        return action, pk, data

    def serialize(self, instance, action):
        payload = {
            "action": action,
            "data": self.serialize_data(instance),
            "model": self.model_label,
        }
        return payload

    def serialize_data(self, instance):
        data = self.get_serializer(instance).data
        only_fields = hasattr(self.get_serializer_class().Meta, 'only_fields')
        if only_fields:
            if self.get_serializer_class().Meta.only_fields != ['all_fields']:
                data = {k: v for k, v in data.items() if k in self.get_serializer_class().Meta.only_fields}
        return data
