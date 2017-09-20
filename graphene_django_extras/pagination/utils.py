# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .pagination import *


def list_pagination_factory(pagination_obj):
    if isinstance(pagination_obj, (LimitOffsetGraphqlPagination, PageGraphqlPagination, CursorGraphqlPagination)):
        return pagination_obj.to_graphql_fields()

    raise ValidationError(_('Incorrect pagination value, it must be instance of: \'LimitOffsetGraphqlPagination\' or '
                            '\'PageGraphqlPagination\' or \'CursorGraphqlPagination\', receive: \'{}\'').
                          format(pagination_obj))
