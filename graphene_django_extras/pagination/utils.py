# -*- coding: utf-8 -*-
from functools import partial

import graphene
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .pagination import *
from ..base_types import DjangoListObjectBase


class GenericPaginationField(graphene.Field):
    """
        Generic pagination field class with all generic function needed to paginate querysets
    """

    def __init__(self, _type, paginator_instance, *args, **kwargs):
        kwargs.setdefault('args', {})

        self.paginator_instance = paginator_instance

        kwargs.update(self.paginator_instance.to_graphql_fields())

        super(GenericPaginationField, self).__init__(graphene.List(_type), *args, **kwargs)

    @property
    def model(self):
        return self.type.of_type._meta.node._meta.model

    def list_resolver(self, manager, root, info, **kwargs):
        if isinstance(root, DjangoListObjectBase):
            return self.paginator_instance.paginate_queryset(root.results, **kwargs)
        return None

    def get_resolver(self, parent_resolver):
        return partial(self.list_resolver, self.type.of_type._meta.model._default_manager)


def _positive_int(integer_string, strict=False, cutoff=None):
    """
    Cast a string to a strictly positive integer.
    """
    if integer_string:
        ret = int(integer_string)
    else:
        return integer_string
    if ret < 0 or (ret == 0 and strict):
        raise ValueError()
    if cutoff:
        return min(ret, cutoff)
    return ret


def _nonzero_int(integer_string, strict=False, cutoff=None):
    """
    Cast a string to a strictly non-zero integer.
    """
    if integer_string:
        ret = int(integer_string)
    else:
        return integer_string
    if ret == 0 and strict:
        raise ValueError()
    if cutoff:
        return min(ret, cutoff)
    return ret

def _get_count(queryset):
    """
    Determine an object count, supporting either querysets or regular lists.
    """
    try:
        return queryset.count()
    except (AttributeError, TypeError):
        return len(queryset)


def list_pagination_factory(pagination_obj):
    if isinstance(pagination_obj, (LimitOffsetGraphqlPagination, PageGraphqlPagination, CursorGraphqlPagination)):
        return pagination_obj.to_graphql_fields()

    raise ValidationError(_('Incorrect pagination value, it must be instance of: \'LimitOffsetGraphqlPagination\' or '
                            '\'PageGraphqlPagination\' or \'CursorGraphqlPagination\', receive: \'{}\'').
                          format(pagination_obj))
