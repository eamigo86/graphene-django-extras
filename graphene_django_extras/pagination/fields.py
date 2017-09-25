# -*- coding: utf-8 -*-
from functools import partial
from math import fabs

from django.utils.translation import ugettext_lazy as _
from graphene import Field, Int, List, NonNull, String, Argument
from graphene_django.utils import maybe_queryset

from ..base_types import DjangoListObjectBase


# *********************************************** #
# ************* PAGINATION FIELDS *************** #
# *********************************************** #
class LimitOffsetPaginationField(Field):

    def __init__(self, _type, page_size=None,
                 limit_query_param='limit', offset_query_param='offset',
                 *args, **kwargs):

        kwargs.setdefault('args', {})

        self.limit_query_param = limit_query_param
        self.offset_query_param = offset_query_param

        kwargs[limit_query_param] = Int(default_value=page_size,
                                        description=_('Number of results to return per page.'))

        kwargs[offset_query_param] = Int(default_value=0,
                                         description=_('The initial index from which to return the results.'))

        super(LimitOffsetPaginationField, self).__init__(List(_type), *args, **kwargs)

    @property
    def model(self):
        return self.type.of_type._meta.node._meta.model

    def list_resolver(self, manager, root, info, **kwargs):
        if isinstance(root, DjangoListObjectBase):
            limit = kwargs.pop(self.limit_query_param, root.count)
            results = root.results
        else:
            qs = manager.get_queryset()
            limit = kwargs.pop(self.limit_query_param, qs.count())
            results = maybe_queryset(qs)

        if limit < 0:
            offset = kwargs.pop(self.offset_query_param, None) or results.count()
            return results[offset - fabs(limit):offset]

        offset = kwargs.pop(self.offset_query_param, 0)
        return results[offset:offset + limit]

    def get_resolver(self, parent_resolver):
        return partial(self.list_resolver, self.type.of_type._meta.model._default_manager)


class PagePaginationField(Field):

    def __init__(self, _type, page_size, page_query_param, page_size_query_param, *args, **kwargs):

        kwargs.setdefault('args', {})

        self.page_query_param = page_query_param or 'page'
        self.page_size = page_size
        self.page_size_query_param = page_size_query_param or 'page_size'

        kwargs[self.page_query_param] = Int(default_value=1,
                                            description=_('A page number within the paginated result set.'))
        if not page_size:
            kwargs[self.page_size_query_param] = NonNull(Int, description=_('Number of results to return per page.'))
        else:
            kwargs[self.page_size_query_param] = Int(description=_('Number of results to return per page.'))

        super(PagePaginationField, self).__init__(List(_type), *args, **kwargs)

    @property
    def model(self):
        return self.type.of_type._meta.node._meta.model

    def list_resolver(self, manager, root, info, **kwargs):
        page = kwargs.pop(self.page_query_param, 1)
        page_size = kwargs.pop(self.page_size_query_param, self.page_size)

        assert page != 0, ValueError('Page value for PageGraphqlPagination must be '
                                     'greater than or leater than that cero')

        if isinstance(root, DjangoListObjectBase):
            result = root.results
        else:
            result = maybe_queryset(manager.get_queryset())

        if page < 0:
            total = result.count()
            offset = int(total - fabs(page_size * page))
        else:
            offset = page_size * (page - 1)

        return result[offset:offset + page_size]

    def get_resolver(self, parent_resolver):
        return partial(self.list_resolver, self.type.of_type._meta.model._default_manager)


class CursorPaginationField(Field):

    def __init__(self, _type, page_size, page_size_query_param, cursor_query_param, ordering,
                 *args, **kwargs):

        kwargs.setdefault('args', {})

        self.cursor_query_param = cursor_query_param
        self.ordering = ordering
        self.page_size = page_size

        kwargs[cursor_query_param] = NonNull(String, description=_('The pagination cursor value.'))

        if page_size_query_param and not page_size:
            self.page_size_query_param = page_size_query_param
            kwargs[page_size_query_param] = NonNull(Int, description=_('Number of results to return per page.'))

        super(CursorPaginationField, self).__init__(List(_type), *args, **kwargs)

    @property
    def model(self):
        return self.type.of_type._meta.node._meta.model

    def list_resolver(self, manager, root, info, **kwargs):
        raise NotImplementedError('{} list_resolver() are not implemented yet.'.format(self.__class__.__name__))

    def get_resolver(self, parent_resolver):
        return partial(self.list_resolver, self.type.of_type._meta.model._default_manager)