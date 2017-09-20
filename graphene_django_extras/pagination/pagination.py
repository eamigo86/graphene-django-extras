# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from graphene import Int, NonNull, String

from .fields import LimitOffsetPaginationField, PagePaginationField, CursorPaginationField

__all__ = ('LimitOffsetGraphqlPagination', 'PageGraphqlPagination', 'CursorGraphqlPagination')


# *********************************************** #
# ************ PAGINATION ClASSES *************** #
# *********************************************** #
class BaseDjangoGraphqlPagination(object):
    page_size = None

    def __init__(self, page_size=None):
        if page_size is None or isinstance(page_size, int):
            self.page_size = page_size
        else:
            raise ValidationError(_('page_size must be integer, receive: {}').format(page_size))

    def get_pagination_field(self, type):
        raise NotImplementedError('get_pagination_class() function must be implemented into child classes.')

    def to_graphql_fields(self):
        raise NotImplementedError('to_graphql_field() function must be implemented into child classes.')

    def to_dict(self):
        return {
            'page_size': self.page_size,
        }

    def paginate_queryset(self, qs, **kwargs):
        raise NotImplementedError('paginate_queryset() function must be implemented into child classes.')


class LimitOffsetGraphqlPagination(BaseDjangoGraphqlPagination):

    def __init__(self, page_size=None, limit_query_param='limit', offset_query_param='offset'):
        super(LimitOffsetGraphqlPagination, self).__init__(page_size)
        self.limit_query_param = limit_query_param
        self.offset_query_param = offset_query_param

    def get_pagination_field(self, type):
        return LimitOffsetPaginationField(type, page_size=self.page_size,
                                          limit_query_param=self.limit_query_param,
                                          offset_query_param=self.offset_query_param)

    def to_dict(self):
        return {
            'limit_query_param': self.limit_query_param,
            'offset_query_param': self.offset_query_param,
            'page_size': self.page_size
        }

    def to_graphql_fields(self):
        return {
            self.limit_query_param: Int(default_value=self.page_size,
                                        description=_('Number of results to return per page.')),
            self.offset_query_param: Int(default_value=0,
                                         description=_('The initial index from which to return the results.'))
        }

    def paginate_queryset(self, qs, **kwargs):
        offset = kwargs.pop(self.offset_query_param, 0)
        limit = kwargs.pop(self.limit_query_param, qs.count())

        return qs[offset:offset + limit]


class PageGraphqlPagination(BaseDjangoGraphqlPagination):

    def __init__(self, page_size=None, page_query_param='page'):
        super(PageGraphqlPagination, self).__init__(page_size)
        self.page_query_param = page_query_param
        self.page_size_query_param = 'page_size' if not page_size else None

    def get_pagination_field(self, type):
        return PagePaginationField(type, page_size=self.page_size,
                                   page_query_param=self.page_query_param,
                                   page_size_query_param=self.page_size_query_param)

    def to_dict(self):
        return {
            'page_query_param': self.page_query_param,
            'page_size_query_param': self.page_size_query_param,
            'page_size': self.page_size
        }

    def to_graphql_fields(self):
        pagination = {
            self.page_query_param: NonNull(Int, default_value=1,
                                           description=_('A page number within the paginated result set.')),
        }

        if self.page_size_query_param and not self.page_size:
            pagination.update({
                self.page_size_query_param: NonNull(Int, description=_('Number of results to return per page.'))
            })

        return pagination

    def paginate_queryset(self, qs, **kwargs):
        page = kwargs.pop(self.page_query_param, 1)

        if self.page_size_query_param:
            page_size = kwargs.pop(self.page_size_query_param, self.page_size)
        else:
            page_size = self.page_size

        offset = page_size * (page - 1)

        return qs[offset:offset + page_size]


class CursorGraphqlPagination(BaseDjangoGraphqlPagination):

    def __init__(self, ordering, page_size=None, cursor_query_param='cursor'):
        super(CursorGraphqlPagination, self).__init__(page_size)
        self.page_size_query_param = 'page_size' if not page_size else None
        self.cursor_query_param = cursor_query_param
        self.ordering = ordering

    def get_pagination_field(self, type):
        return CursorPaginationField(type, page_size=self.page_size,
                                     cursor_query_param=self.cursor_query_param,
                                     page_size_query_param=self.page_size_query_param,
                                     ordering=self.ordering)

    def to_dict(self):
        return {
            'cursor_query_param': self.cursor_query_param,
            'page_size_query_param': self.page_size_query_param,
            'page_size': self.page_size,
            'ordering': self.ordering
        }

    def to_graphql_fields(self):
        pagination = {
            self.cursor_query_param: NonNull(String, description=_('The pagination cursor value.'))
        }

        if self.page_size_query_param and not self.page_size:
            pagination.update({
                self.page_size_query_param: NonNull(Int, description=_('Number of results to return per page.'))
            })

        return pagination

    def paginate_queryset(self, qs, **kwargs):
        raise NotImplementedError('paginate_queryset() on CursorGraphqlPagination are not implemented yet.')
