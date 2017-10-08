# -*- coding: utf-8 -*-
from graphene.utils.str_converters import to_camel_case


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
