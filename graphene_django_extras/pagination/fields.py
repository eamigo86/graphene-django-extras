# -*- coding: utf-8 -*-
from functools import partial

from django.utils.translation import ugettext_lazy as _
from graphene import Field, Int, List, NonNull, String
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
        offset = kwargs.pop(self.offset_query_param, 0)

        if isinstance(root, DjangoListObjectBase):
            limit = kwargs.pop(self.limit_query_param, root.count)
            return root.results[offset:offset + limit]
        else:
            qs = manager.get_queryset()
            limit = kwargs.pop(self.limit_query_param, qs.count())
            return maybe_queryset(qs[offset:offset + limit])

    def get_resolver(self, parent_resolver):
        return partial(self.list_resolver, self.type.of_type._meta.model._default_manager)


class PagePaginationField(Field):

    def __init__(self, _type, page_size, page_query_param, page_size_query_param, *args, **kwargs):

        kwargs.setdefault('args', {})

        self.page_query_param = page_query_param
        self.page_size = page_size

        kwargs[page_query_param] = NonNull(Int, default_value=1,
                                           description=_('A page number within the paginated result set.'))
        if page_size_query_param and not page_size:
            self.page_size_query_param = page_size_query_param
            kwargs[page_size_query_param] = NonNull(Int, description=_('Number of results to return per page.'))

        super(PagePaginationField, self).__init__(List(_type), *args, **kwargs)

    @property
    def model(self):
        return self.type.of_type._meta.node._meta.model

    def list_resolver(self, manager, root, info, **kwargs):
        page = kwargs.pop(self.page_query_param, 1)

        if getattr(self, 'page_size_query_param', None):
            page_size = kwargs.pop(self.page_size_query_param, self.page_size)
        else:
            page_size = self.page_size

        offset = page_size * (page - 1)

        if isinstance(root, DjangoListObjectBase):
            return root.results[offset:offset + page_size]
        else:
            qs = manager.get_queryset()
            return maybe_queryset(qs[offset:offset + page_size])

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