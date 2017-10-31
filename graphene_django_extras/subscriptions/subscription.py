# -*- coding: utf-8 -*-
import copy
import json

from channels import Group
from graphene import Field, Argument, Enum, String, ObjectType, Boolean, List, ID
from graphene.types.base import BaseOptions
from graphene.utils.str_converters import to_snake_case
from six import string_types

from ..mutation import DjangoSerializerMutation
from .bindings import SubscriptionResourceBinding


class ActionSubscriptionEnum(Enum):
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
    ALL_ACTIONS = 'all_actions'


class OperationSubscriptionEnum(Enum):
    SUBSCRIBE = 'subscribe'
    UNSUBSCRIBE = 'unsubscribe'


class SubscriptionOptions(BaseOptions):
    output = None
    fields = None
    arguments = None
    model = None
    stream = None
    serializer_class = None
    queryset = None
    mutation_class = None


class Subscription(ObjectType):
    """
        Subscription Type Definition
    """
    ok = Boolean(description='Boolean field that return subscription request result.')
    error = String(description='Subscribe or unsubscribe operation request error .')
    stream = String(description='Stream name.')
    operation = OperationSubscriptionEnum(description='Subscription operation.')
    action = ActionSubscriptionEnum(description='Subscription action.')

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, mutation_class=None, stream=None, queryset=None, description='', **options):

        assert issubclass(mutation_class, DjangoSerializerMutation), \
            'You need to pass a valid DjangoSerializerMutation subclass in {}.Meta, received "mutation_class = {}"'\
            .format(cls.__name__, mutation_class)

        assert isinstance(stream, string_types), \
            'You need to pass a valid string stream name in {}.Meta, received "{}"'.format(
                cls.__name__, stream)

        if queryset:
            assert mutation_class._meta.model == queryset.model, \
                'The queryset model must correspond with the mutation_class model passed on Meta class, received ' \
                '"{}", expected "{}"'.format(queryset.model.__name__, mutation_class._meta.model.__name__)

        description = description or 'Subscription Type for {} model'.format(mutation_class._meta.model.__name__)

        _meta = SubscriptionOptions(cls)

        _meta.output = cls
        _meta.fields = None
        _meta.model = mutation_class._meta.model
        _meta.stream = stream
        _meta.serializer_class = copy.deepcopy(mutation_class._meta.serializer_class)
        _meta.mutation_class = mutation_class

        serializer_fields = [(to_snake_case(field.strip('_')).upper(), to_snake_case(field))
                             for field in _meta.serializer_class.Meta.fields]
        model_fields_enum = Enum('{}Fields'.format(mutation_class._meta.model.__name__), serializer_fields,
                                 description='Desired {} fields in subscription\'s  notification.'
                                 .format(mutation_class._meta.model.__name__))

        arguments = {
            'channel_id': Argument(String, required=True, description='Websocket\'s channel connection identification'),
            'action': Argument(ActionSubscriptionEnum, required=True,
                               description='Subscribe or unsubscribe action : (create, update or delete)'),
            'operation': Argument(OperationSubscriptionEnum, required=True, description='Operation to do'),
            'id': Argument(ID, description='ID field value that has the object to which you wish to subscribe'),
            'data': List(model_fields_enum, required=False)
        }

        _meta.arguments = arguments

        super(Subscription, cls).__init_subclass_with_meta__(_meta=_meta, description=description, **options)

    @classmethod
    def model_label(cls):
        return u'{}.{}'.format(cls._meta.model._meta.app_label.lower(), cls._meta.model._meta.object_name.lower())

    @classmethod
    def _group_name(cls, action, id=None):
        """ Formatting helper for group names. """
        if id:
            # return '{}-{}-{}-{}'.format(cls.model_label(), cls._meta.stream.lower(), action, id)
            return '{}-{}-{}'.format(cls.model_label(), action, id)
        else:
            # return '{}-{}-{}'.format(cls.model_label(), cls._meta.stream.lower(), action)
            return '{}-{}'.format(cls.model_label(), action)

    @classmethod
    def subscription_resolver(cls, root, info, **kwargs):
        # Manage the subscribe or unsubscribe operations
        action = kwargs.get('action')
        operation = kwargs.get('operation')
        data = kwargs.get('data', None)
        obj_id = kwargs.get('id', None)

        response = {
            'stream': cls._meta.stream,
            'operation': operation,
            'action': action
        }

        try:
            channel = copy.copy(info.context.reply_channel)
            channel.name = u'daphne.response.{}'.format(kwargs.get('channel_id'))

            if action == 'all_actions':
                for act in ('create', 'update', 'delete'):
                    group_name = cls._group_name(act, id=obj_id)

                    if operation == 'subscribe':
                        Group(group_name).add(channel)
                    elif operation == 'unsubscribe':
                        Group(group_name).discard(channel)
            else:
                group_name = cls._group_name(action, id=obj_id)

                if operation == 'subscribe':
                    Group(group_name).add(channel)
                elif operation == 'unsubscribe':
                    Group(group_name).discard(channel)

            if data is not None:
                setattr(cls._meta.serializer_class.Meta, 'only_fields', data)

            response.update(dict(ok=True, error=None))
            channel.send({'text': json.dumps(response)})

        except Exception as e:
            response.update(dict(ok=False, error=e.__str__()))

        return cls(**response)

    @classmethod
    def get_binding(cls):

        class ResourceBinding(SubscriptionResourceBinding):
            model = cls._meta.model
            stream = cls._meta.stream
            serializer_class = cls._meta.serializer_class
            queryset = cls._meta.queryset

        return ResourceBinding

    @classmethod
    def Field(cls, *args, **kwargs):
        kwargs.update({'description': 'Subscription for {} model'.format(cls._meta.model.__name__)})
        return Field(cls._meta.output, args=cls._meta.arguments, resolver=cls.subscription_resolver, **kwargs)
