# -*- coding: utf-8 -*-
from graphene.utils.str_converters import to_camel_case


class Registry(object):
    """
        Custom registry implementation for use on DjangoObjectType and DjangoInputObjectType
    """
    def __init__(self):
        self._registry = {}
        self._registry_models = {}

    def register(self, cls, for_input=False):
        from .types import DjangoInputObjectType, DjangoObjectType
        assert issubclass(
            cls, (DjangoInputObjectType, DjangoObjectType)), 'Only DjangoInputObjectType or DjangoObjectType can be' \
                                                             ' registered, received "{}"'.format(cls.__name__)
                                                             
        assert cls._meta.registry == self, 'Registry for a Model have to match.'

        if not getattr(cls._meta, 'skip_registry', False):
            key = '{}_Input'.format(cls._meta.model.__name__.lower()) \
                if for_input else cls._meta.model.__name__.lower()
            self._registry[to_camel_case(key)] = cls

    def get_type_for_model(self, model):
        return self._registry.get(model.__name__.lower())


registry = None


def get_global_registry():
    global registry
    if not registry:
        registry = Registry()
    return registry


def reset_global_registry():
    global registry
    registry = None