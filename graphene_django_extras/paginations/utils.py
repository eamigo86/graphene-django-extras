# -*- coding: utf-8 -*-
from functools import partial

import graphene
from django.db import DatabaseError

from ..base_types import DjangoListObjectBase


class GenericPaginationField(graphene.Field):
    """
        Generic paginations field class with all generic function needed to paginate queryset
    """

    def __init__(self, _type, paginator_instance, *args, **kwargs):
        kwargs.setdefault("args", {})

        self.paginator_instance = paginator_instance

        kwargs.update(self.paginator_instance.to_graphql_fields())
        kwargs.update(
            {
                "description": "{} list, paginated by {}".format(
                    _type._meta.model.__name__, paginator_instance.__name__
                )
            }
        )

        super(GenericPaginationField, self).__init__(
            graphene.List(_type), *args, **kwargs
        )

    @property
    def model(self):
        return self.type.of_type._meta.node._meta.model

    def list_resolver(self, manager, root, info, **kwargs):
        if isinstance(root, DjangoListObjectBase):
            return self.paginator_instance.paginate_queryset(root.results, **kwargs)
        return None

    def get_resolver(self, parent_resolver):
        return partial(
            self.list_resolver, self.type.of_type._meta.model._default_manager
        )


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
    except (AttributeError, TypeError, DatabaseError):
        return len(queryset)
