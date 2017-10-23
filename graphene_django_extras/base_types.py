# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime
import graphene

from graphene import Scalar
from graphene.utils.str_converters import to_camel_case
from graphql.language import ast

try:
    import iso8601
except:
    raise ImportError(
        "iso8601 package is required for DateTime Scalar.\n"
        "You can install it using: pip install iso8601."
    )


class Date(Scalar):
    '''
    The `Date` scalar type represents a Date
    value as specified by
    [iso8601](https://en.wikipedia.org/wiki/ISO_8601).
    '''
    epoch_time = '00:00:00'

    @staticmethod
    def serialize(date):
        assert isinstance(date, datetime.date), (
            'Received not compatible date "{}"'.format(repr(date))
        )
        return date.isoformat()

    @classmethod
    def parse_literal(cls, node):
        if isinstance(node, ast.StringValue):
            return cls.parse_value(node.value)

    @classmethod
    def parse_value(cls, value):
        dt = iso8601.parse_date('{}T{}'.format(value, cls.epoch_time))
        return datetime.date(dt.year, dt.month, dt.day)


def generic_django_object_type_factory(graphene_type, new_model, new_only_fields=(), new_exclude_fields=(),
                                       new_filter_fields=None, new_registry=None, new_skip_registry=False):

    class GenericType(graphene_type):
        class Meta:
            model = new_model
            name = to_camel_case('{}_Generic_Type'.format(new_model.__name__))
            only_fields = new_only_fields
            exclude_fields = new_exclude_fields
            filter_fields = new_filter_fields
            registry = new_registry
            skip_registry = new_skip_registry

    return GenericType


def generic_django_input_object_type_factory(graphene_input_type, new_model, new_input_for,
                                             new_only_fields=(), new_exclude_fields=(), new_filter_fields=None,
                                             new_nested_fields=False, new_registry=None, new_skip_registry=False):

    class GenericInputType(graphene_input_type):
        class Meta:
            model = new_model
            name = to_camel_case('{}_{}_Generic_Type'.format(new_model.__name__, new_input_for))
            only_fields = new_only_fields
            exclude_fields = new_exclude_fields
            filter_fields = new_filter_fields
            nested_fields = new_nested_fields
            registry = new_registry
            skip_registry = new_skip_registry
            input_for = new_input_for

    return GenericInputType


class DjangoListObjectBase(object):
    def __init__(self, results, count, results_field_name='results'):
        self.results = results
        self.count = count
        self.results_field_name = results_field_name

    def to_dict(self):
        return {
            self.results_field_name: [e.to_dict() for e in self.results],
            'count': self.count,
        }


def resolver(attr_name, root, instance, info):
    if attr_name == 'app_label':
        return instance._meta.app_label
    elif attr_name == 'id':
        return instance.id
    elif attr_name == 'model_name':
        return instance._meta.model.__name__


class GenericForeignKeyType(graphene.ObjectType):
    app_label = graphene.String()
    id = graphene.ID()
    model_name = graphene.String()

    class Meta:
        description = " Type for a GenericForeignKey relation "
        default_resolver = resolver


class GenericForeignKeyInputType(graphene.InputObjectType):
    app_label = graphene.Argument(graphene.String, required=True)
    id = graphene.Argument(graphene.ID, required=True)
    model_name = graphene.Argument(graphene.String, required=True)

    class Meta:
        description = " Input Type for a GenericForeignKey relation "
