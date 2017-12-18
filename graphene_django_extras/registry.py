# -*- coding: utf-8 -*-
from graphene.utils.str_converters import to_camel_case


class Registry(object):
    """
        Custom registry implementation for use on DjangoObjectType and DjangoInputObjectType
    """
    def __init__(self):
        self._registry = {}
        self._registry_models = {}
        self._registry_directives = {}

    def register_enum(self, key, enum):
        self._registry[key] = enum

    def get_type_for_enum(self, key):
        return self._registry.get(key)

    def register_directive(self, name, directive):
        self._registry_directives[name] = directive

    def get_directive(self, name):
        return self._registry_directives.get(name)

    def register(self, cls, for_input=None):
        from .types import DjangoInputObjectType, DjangoObjectType
        assert issubclass(
            cls, (DjangoInputObjectType, DjangoObjectType)), 'Only DjangoInputObjectType or DjangoObjectType can be' \
                                                             ' registered, received "{}"'.format(cls.__name__)

        assert cls._meta.registry == self, 'Registry for a Model have to match.'

        if not getattr(cls._meta, 'skip_registry', False):
            key = '{}_{}'.format(cls._meta.model.__name__.lower(), for_input) \
                if for_input else cls._meta.model.__name__.lower()
            self._registry[to_camel_case(key)] = cls

    def get_type_for_model(self, model, for_input=None):
        key = '{}_{}'.format(model.__name__.lower(), for_input) if for_input else model.__name__.lower()
        return self._registry.get(to_camel_case(key))


registry = None


def get_global_registry():
    global registry
    if not registry:
        registry = Registry()
    return registry


def reset_global_registry():
    global registry
    registry = None
