# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime

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

    @staticmethod
    def serialize(dt):
        assert isinstance(dt, datetime.date), (
            'Received not compatible date "{}"'.format(repr(dt))
        )
        return dt.isoformat()

    @classmethod
    def parse_literal(cls, node):
        if isinstance(node, ast.StringValue):
            return cls.parse_value(node.value).date()

    @staticmethod
    def parse_value(value):
        return iso8601.parse_date(value)


def generic_django_object_type_factory(graphene_type, new_model, new_only_fields=(), new_exclude_fields=(),
                                       new_filter_fields=None, new_registry=None, new_skip_registry=False):

    class GenericType(graphene_type):
        class Meta:
            model = new_model
            name = to_camel_case('{}_Type'.format(new_model.__name__))
            only_fields = new_only_fields
            exclude_fields = new_exclude_fields
            filter_fields = new_filter_fields
            registry = new_registry
            skip_registry = new_skip_registry

    return GenericType


def generic_django_input_object_type_factory(graphene_input_type, new_model, new_input_for, new_only_fields=(),
                                             new_exclude_fields=(), new_filter_fields=None, new_nested_fields=False,
                                             new_registry=None, new_skip_registry=False):

    class GenericInputType(graphene_input_type):
        class Meta:
            model = new_model
            name = to_camel_case('{}_{}_Type'.format(new_model.__name__, new_input_for))
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
