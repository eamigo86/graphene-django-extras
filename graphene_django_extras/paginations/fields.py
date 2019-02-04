# -*- coding: utf-8 -*-
from functools import partial
from math import fabs

from graphene import Field, Int, List, NonNull, String

from .utils import _nonzero_int, _get_count
from ..settings import graphql_api_settings

__all__ = ("LimitOffsetPaginationField", "PagePaginationField", "CursorPaginationField")


class AbstractPaginationField(Field):
    @property
    def model(self):
        return self.type.of_type._meta.node._meta.model

    def get_resolver(self, parent_resolver):
        return partial(
            self.list_resolver, self.type.of_type._meta.model._default_manager
        )


# *********************************************** #
# ************* PAGINATION FIELDS *************** #
# *********************************************** #
class LimitOffsetPaginationField(AbstractPaginationField):
    def __init__(
        self,
        _type,
        default_limit=graphql_api_settings.DEFAULT_PAGE_SIZE,
        max_limit=graphql_api_settings.MAX_PAGE_SIZE,
        ordering="",
        limit_query_param="limit",
        offset_query_param="offset",
        ordering_param="order",
        *args,
        **kwargs,
    ):

        kwargs.setdefault("args", {})

        self.limit_query_param = limit_query_param
        self.offset_query_param = offset_query_param
        self.ordering_param = ordering_param
        self.max_limit = max_limit
        self.default_limit = default_limit
        self.ordering = ordering

        kwargs[limit_query_param] = Int(
            default_value=self.default_limit,
            description="Number of results to return per page. Actual "
            "'default_limit': {}, and 'max_limit': {}".format(
                self.default_limit, self.max_limit
            ),
        )

        kwargs[offset_query_param] = Int(
            default_value=0,
            description="The initial index from which to return the results.",
        )

        kwargs[ordering_param] = String(
            default_value="",
            description="A string or comma delimited string values that indicate the "
            "default ordering when obtaining lists of objects.",
        )

        super(LimitOffsetPaginationField, self).__init__(List(_type), *args, **kwargs)

    def list_resolver(self, manager, root, info, **kwargs):
        qs = manager.get_queryset()
        count = _get_count(qs)
        limit = _nonzero_int(
            kwargs.get(self.limit_query_param, None), strict=True, cutoff=self.max_limit
        )

        order = kwargs.pop(self.ordering_param, None) or self.ordering
        if order:
            if "," in order:
                order = order.strip(",").replace(" ", "").split(",")
                if order.__len__() > 0:
                    qs = qs.order_by(*order)
            else:
                qs = qs.order_by(order)

        if limit < 0:
            offset = kwargs.pop(self.offset_query_param, None) or count
            return qs[offset - fabs(limit) : offset]

        offset = kwargs.pop(self.offset_query_param, 0)
        return qs[offset : offset + limit]


class PagePaginationField(AbstractPaginationField):
    def __init__(
        self,
        _type,
        page_size=graphql_api_settings.DEFAULT_PAGE_SIZE,
        page_size_query_param=None,
        max_page_size=graphql_api_settings.MAX_PAGE_SIZE,
        ordering="",
        ordering_param="order",
        *args,
        **kwargs,
    ):

        kwargs.setdefault("args", {})

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

        self.ordering = ordering

        self.ordering_param = ordering_param

        self.page_size_query_description = "Number of results to return per page. Actual 'page_size': {}".format(
            self.page_size
        )

        kwargs[self.page_query_param] = Int(
            default_value=1,
            description="A page number within the result paginated set. Default: 1",
        )

        kwargs[self.ordering_param] = String(
            default_value="",
            description="A string or coma separate strings values that indicating the "
            "default ordering when obtaining lists of objects.",
        )

        if self.page_size_query_param:
            if not page_size:
                kwargs[self.page_size_query_param] = NonNull(
                    Int, description=self.page_size_query_description
                )
            else:
                kwargs[self.page_size_query_param] = Int(
                    description=self.page_size_query_description
                )

        super(PagePaginationField, self).__init__(List(_type), *args, **kwargs)

    def list_resolver(self, manager, root, info, **kwargs):
        qs = manager.get_queryset()
        count = _get_count(qs)
        page = kwargs.pop(self.page_query_param, 1)
        if self.page_size_query_param:
            page_size = _nonzero_int(
                kwargs.get(self.page_size_query_param, None),
                strict=True,
                cutoff=self.max_page_size,
            )
        else:
            page_size = self.page_size

        assert page != 0, ValueError(
            "Page value for PageGraphqlPagination must be "
            "greater than or smaller than that zero, not a zero value"
        )

        assert page_size > 0, ValueError(
            "Page_size value for PageGraphqlPagination must be a non-null value, you must"
            " set global DEFAULT_PAGE_SIZE on GRAPHENE_DJANGO_EXTRAS dict on your"
            " settings.py or specify a page_size_query_param value on paginations "
            "declaration to specify a custom page size value through a query parameters"
        )

        offset = (
            int(count - fabs(page_size * page)) if page < 0 else page_size * (page - 1)
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


class CursorPaginationField(AbstractPaginationField):
    def __init__(
        self, _type, ordering="-created", cursor_query_param="cursor", *args, **kwargs
    ):
        kwargs.setdefault("args", {})

        self.page_size = graphql_api_settings.DEFAULT_PAGE_SIZE
        self.page_size_query_param = "page_size" if not self.page_size else None
        self.cursor_query_param = cursor_query_param
        self.ordering = ordering
        self.cursor_query_description = "The pagination cursor value."
        self.page_size_query_description = "Number of results to return per page."

        kwargs[self.cursor_query_param] = NonNull(
            String, description=self.cursor_query_description
        )

        if self.page_size_query_param:
            if not self.page_size:
                kwargs[self.page_size_query_param] = NonNull(
                    Int, description=self.page_size_query_description
                )
            else:
                kwargs[self.page_size_query_param] = Int(
                    description=self.page_size_query_description
                )

        super(CursorPaginationField, self).__init__(List(_type), *args, **kwargs)

    def list_resolver(self, manager, root, info, **kwargs):
        raise NotImplementedError(
            "{} list_resolver() are not implemented yet.".format(
                self.__class__.__name__
            )
        )
