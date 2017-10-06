# -*- coding: utf-8 -*-
from math import fabs

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from graphene import Int, NonNull, String

from .fields import LimitOffsetPaginationField, PagePaginationField, CursorPaginationField
from .utils import _get_count, GenericPaginationField, _nonzero_int
from ..settings import graphql_api_settings

__all__ = ('LimitOffsetGraphqlPagination', 'PageGraphqlPagination', 'CursorGraphqlPagination')


# *********************************************** #
# ************ PAGINATION ClASSES *************** #
# *********************************************** #
class BaseDjangoGraphqlPagination(object):
    _field = None

    @property
    def get_field(self):
        return self._field

    def get_pagination_field(self, type):
        return GenericPaginationField(type, paginator_instance=self)

    def to_graphql_fields(self):
        raise NotImplementedError('to_graphql_field() function must be implemented into child classes.')

    def to_dict(self):
        raise NotImplementedError('to_dict() function must be implemented into child classes.')

    def paginate_queryset(self, qs, **kwargs):
        raise NotImplementedError('paginate_queryset() function must be implemented into child classes.')


class LimitOffsetGraphqlPagination(BaseDjangoGraphqlPagination):

    def __init__(self, default_limit=graphql_api_settings.PAGE_SIZE, max_limit=None,
                 limit_query_param='limit', offset_query_param='offset'):

        self._field = LimitOffsetPaginationField

        # A numeric value indicating the limit to use if one is not provided by the client in a query parameter.
        self.default_limit = default_limit

        # If set this is a numeric value indicating the maximum allowable limit that may be requested by the client.
        self.max_limit = max_limit

        # A string value indicating the name of the "limit" query parameter.
        self.limit_query_param = limit_query_param

        # A string value indicating the name of the "offset" query parameter.
        self.offset_query_param = offset_query_param

        self.limit_query_description = _('Number of results to return per page. Default \'default_limit\': {}, and '
                                         '\'max_limit\': {}').format(self.default_limit, self.max_limit)
        self.offset_query_description = _('The initial index from which to return the results. Default: 0')

    def to_dict(self):
        return {
            'limit_query_param': self.limit_query_param,
            'offset_query_param': self.offset_query_param,
            'default_limit': self.default_limit,
            'max_limit': self.max_limit
        }

    def to_graphql_fields(self):
        return {
            self.limit_query_param: Int(default_value=self.default_limit,
                                        description=self.limit_query_description),
            self.offset_query_param: Int(description=self.offset_query_description)
        }

    def paginate_queryset(self, qs, **kwargs):
        count = _get_count(qs)
        limit = _nonzero_int(
            kwargs.get(self.limit_query_param, None),
            strict=True,
            cutoff=self.max_limit
        )

        if limit is None:
            return None

        if limit < 0:
            offset = kwargs.get(self.offset_query_param, count) + limit
        else:
            offset = kwargs.get(self.offset_query_param, 0)

        if count == 0 or offset > count or offset < 0:
            return []

        return qs[offset:offset + fabs(limit)]


class PageGraphqlPagination(BaseDjangoGraphqlPagination):

    def __init__(self, page_size=graphql_api_settings.PAGE_SIZE, page_size_query_param=None,
                 max_page_size=None):

        self._field = PagePaginationField

        # Client can control the page using this query parameter.
        self.page_query_param = 'page'

        # The default page size. Defaults to `None`.
        self.page_size = page_size

        # Client can control the page size using this query parameter.
        # Default is 'None'. Set to eg 'page_size' to enable usage.
        self.page_size_query_param = page_size_query_param

        # Set to an integer to limit the maximum page size the client may request.
        # Only relevant if 'page_size_query_param' has also been set.
        self.max_page_size = max_page_size

        self.page_size_query_description = _('Number of results to return per page. Default \'page_size\': {}').format(
            self.page_size)

        self.page_query_description = _('A page number within the paginated result set. Default: 1')

    def to_dict(self):
        return {
            'page_size': self.page_size,
            'page_query_param': self.page_query_param,
            'page_size_query_param': self.page_size_query_param,
            'max_page_size': self.max_page_size
        }

    def to_graphql_fields(self):
        paginator_dict = {
            self.page_query_param: Int(default_value=1, description=self.page_query_description),
        }

        if self.page_size_query_param:
            paginator_dict.update({
                self.page_size_query_param: Int(description=self.page_size_query_description)
            })

        return paginator_dict

    def paginate_queryset(self, qs, **kwargs):
        count = _get_count(qs)
        page = kwargs.pop(self.page_query_param, 1)
        if self.page_size_query_param:
            page_size = _nonzero_int(
                kwargs.get(self.page_size_query_param, None),
                strict=True,
                cutoff=self.max_page_size
            )
        else:
            page_size = self.page_size

        assert page != 0, ValueError('Page value for PageGraphqlPagination must be a non-zero value')
        if page_size is None:
            """
            raise ValueError('Page_size value for PageGraphqlPagination must be a non-null value, you must set global'
                             ' PAGE_SIZE on GRAPHENE_DJANGO_EXTRAS dict on your settings.py or specify a '
                             'page_size_query_param value on pagination declaration to specify a custom page size '
                             'value through a query parameters')
            """
            return None

        offset = max(0, int(count + page_size * page)) if page < 0 else page_size * (page - 1)

        return qs[offset:offset + page_size]


class CursorGraphqlPagination(BaseDjangoGraphqlPagination):
    cursor_query_description = _('The pagination cursor value.')
    page_size = graphql_api_settings.PAGE_SIZE

    def __init__(self, ordering='-created', cursor_query_param='cursor'):
        self._field = CursorPaginationField

        self.page_size_query_param = 'page_size' if not self.page_size else None
        self.cursor_query_param = cursor_query_param
        self.ordering = ordering

    def to_dict(self):
        return {
            'page_size_query_param': self.page_size_query_param,
            'cursor_query_param': self.cursor_query_param,
            'ordering': self.ordering,
            'page_size': self.page_size
        }

    def to_graphql_fields(self):
        return {
            self.cursor_query_param: NonNull(String, description=self.cursor_query_description)
        }

    def paginate_queryset(self, qs, **kwargs):
        raise NotImplementedError('paginate_queryset() on CursorGraphqlPagination are not implemented yet.')
