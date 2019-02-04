# -*- coding: utf-8 -*-
from math import fabs

from graphene import Int, NonNull, String

from graphene_django_extras.paginations.utils import (
    _get_count,
    GenericPaginationField,
    _nonzero_int,
)
from graphene_django_extras.settings import graphql_api_settings

__all__ = (
    "LimitOffsetGraphqlPagination",
    "PageGraphqlPagination",
    "CursorGraphqlPagination",
)


# *********************************************** #
# ************ PAGINATION ClASSES *************** #
# *********************************************** #
class BaseDjangoGraphqlPagination(object):
    __name__ = None

    def get_pagination_field(self, type):
        return GenericPaginationField(type, paginator_instance=self)

    def to_graphql_fields(self):
        raise NotImplementedError(
            "to_graphql_field() function must be implemented into child classes."
        )

    def to_dict(self):
        raise NotImplementedError(
            "to_dict() function must be implemented into child classes."
        )

    def paginate_queryset(self, qs, **kwargs):
        raise NotImplementedError(
            "paginate_queryset() function must be implemented into child classes."
        )


class LimitOffsetGraphqlPagination(BaseDjangoGraphqlPagination):
    __name__ = "LimitOffsetPaginator"

    def __init__(
        self,
        default_limit=graphql_api_settings.DEFAULT_PAGE_SIZE,
        max_limit=graphql_api_settings.MAX_PAGE_SIZE,
        ordering="",
        limit_query_param="limit",
        offset_query_param="offset",
        ordering_param="ordering",
    ):

        # A numeric value indicating the limit to use if one is not provided by the client in a query parameter.
        self.default_limit = default_limit

        # If set this is a numeric value indicating the maximum allowable limit that may be requested by the client.
        self.max_limit = max_limit

        # Default ordering value: ""
        self.ordering = ordering

        # A string value indicating the name of the "limit" query parameter.
        self.limit_query_param = limit_query_param

        # A string value indicating the name of the "offset" query parameter.
        self.offset_query_param = offset_query_param

        # A string or tuple/list of strings that indicating the default ordering when obtaining lists of objects.
        # Uses Django order_by syntax
        self.ordering_param = ordering_param

    def to_dict(self):
        return {
            "limit_query_param": self.limit_query_param,
            "default_limit": self.default_limit,
            "max_limit": self.max_limit,
            "offset_query_param": self.offset_query_param,
            "ordering_param": self.ordering_param,
            "ordering": self.ordering,
        }

    def to_graphql_fields(self):
        return {
            self.limit_query_param: Int(
                default_value=self.default_limit,
                description="Number of results to return per page. Default "
                "'default_limit': {}, and 'max_limit': {}".format(
                    self.default_limit, self.max_limit
                ),
            ),
            self.offset_query_param: Int(
                description="The initial index from which to return the results. Default: 0"
            ),
            self.ordering_param: String(
                description="A string or comma delimited string values that indicate the "
                "default ordering when obtaining lists of objects."
            ),
        }

    def paginate_queryset(self, qs, **kwargs):
        limit = _nonzero_int(
            kwargs.get(self.limit_query_param, None), strict=True, cutoff=self.max_limit
        )

        if limit is None:
            return qs

        order = kwargs.pop(self.ordering_param, None) or self.ordering
        if order:
            if "," in order:
                order = order.strip(",").replace(" ", "").split(",")
                if order.__len__() > 0:
                    qs = qs.order_by(*order)
            else:
                qs = qs.order_by(order)

        offset = kwargs.get(self.offset_query_param, 0)

        return qs[offset : offset + fabs(limit)]


class PageGraphqlPagination(BaseDjangoGraphqlPagination):
    __name__ = "PagePaginator"

    def __init__(
        self,
        page_size=graphql_api_settings.DEFAULT_PAGE_SIZE,
        page_size_query_param=None,
        max_page_size=graphql_api_settings.MAX_PAGE_SIZE,
        ordering="",
        ordering_param="ordering",
    ):

        # Client can control the page using this query parameter.
        self.page_query_param = "page"

        # The default page size. Defaults to `None`.
        self.page_size = page_size

        # Client can control the page size using this query parameter.
        # Default is 'None'. Set to eg 'page_size' to enable usage.
        self.page_size_query_param = page_size_query_param

        # Set to an integer to limit the maximum page size the client may request.
        # Only relevant if 'page_size_query_param' has also been set.
        self.max_page_size = max_page_size

        # Default ordering value: ""
        self.ordering = ordering

        # A string or comma delimited string values that indicate the default ordering when obtaining lists of objects.
        # Uses Django order_by syntax
        self.ordering_param = ordering_param

        self.page_size_query_description = "Number of results to return per page. Default 'page_size': {}".format(
            self.page_size
        )

    def to_dict(self):
        return {
            "page_size_query_param": self.page_size_query_param,
            "page_size": self.page_size,
            "page_query_param": self.page_query_param,
            "max_page_size": self.max_page_size,
            "ordering_param": self.ordering_param,
            "ordering": self.ordering,
        }

    def to_graphql_fields(self):
        paginator_dict = {
            self.page_query_param: Int(
                default_value=1,
                description="A page number within the result paginated set. Default: 1",
            ),
            self.ordering_param: String(
                description="A string or comma delimited string values that indicate the "
                "default ordering when obtaining lists of objects."
            ),
        }

        if self.page_size_query_param:
            paginator_dict.update(
                {
                    self.page_size_query_param: Int(
                        description=self.page_size_query_description
                    )
                }
            )

        return paginator_dict

    def paginate_queryset(self, qs, **kwargs):
        count = _get_count(qs)
        page = kwargs.pop(self.page_query_param, 1)
        if self.page_size_query_param:
            page_size = _nonzero_int(
                kwargs.get(self.page_size_query_param, self.page_size),
                strict=True,
                cutoff=self.max_page_size,
            )
        else:
            page_size = self.page_size

        assert page != 0, ValueError(
            "Page value for PageGraphqlPagination must be a non-zero value"
        )
        if page_size is None:
            """
            raise ValueError('Page_size value for PageGraphqlPagination must be a non-null value, you must set global'
                             ' DEFAULT_PAGE_SIZE on GRAPHENE_DJANGO_EXTRAS dict on your settings.py or specify a '
                             'page_size_query_param value on paginations declaration to specify a custom page size '
                             'value through a query parameters')
            """
            return None

        offset = (
            max(0, int(count + page_size * page))
            if page < 0
            else page_size * (page - 1)
        )

        order = kwargs.pop(self.ordering_param, None) or self.ordering
        if order:
            if "," in order:
                order = order.strip(",").replace(" ", "").split(",")
                if order.__len__() > 0:
                    qs = qs.order_by(*order)
            else:
                qs = qs.order_by(order)

        return qs[offset : offset + page_size]


class CursorGraphqlPagination(BaseDjangoGraphqlPagination):
    __name__ = "CursorPaginator"
    cursor_query_description = "The pagination cursor value."
    page_size = graphql_api_settings.DEFAULT_PAGE_SIZE

    def __init__(self, ordering="-created", cursor_query_param="cursor"):

        self.page_size_query_param = "page_size" if not self.page_size else None
        self.cursor_query_param = cursor_query_param
        self.ordering = ordering

    def to_dict(self):
        return {
            "page_size_query_param": self.page_size_query_param,
            "cursor_query_param": self.cursor_query_param,
            "ordering": self.ordering,
            "page_size": self.page_size,
        }

    def to_graphql_fields(self):
        return {
            self.cursor_query_param: NonNull(
                String, description=self.cursor_query_description
            )
        }

    def paginate_queryset(self, qs, **kwargs):
        raise NotImplementedError(
            "paginate_queryset() on CursorGraphqlPagination are not implemented yet."
        )
