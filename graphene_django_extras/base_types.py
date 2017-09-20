# -*- coding: utf-8 -*-


def generic_django_object_type_factory(graphene_type, new_model, new_only_fields=(), new_exclude_fields=(),
                                       new_filter_fields=None):
    class GenericType(graphene_type):
        class Meta:
            model = new_model
            name = '{}Type'.format(new_model.__name__)
            only_fields = new_only_fields
            exclude_fields = new_exclude_fields
            filter_fields = new_filter_fields

    return GenericType


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
