# -*- coding: utf-8 -*-
"""GraphQL Django Extras - Additional tools and utilities for graphene-django."""
from graphene.pyutils.version import get_version

from .directives import all_directives
from .fields import (
    DjangoFilterListField,
    DjangoFilterPaginateListField,
    DjangoListObjectField,
    DjangoObjectField,
)
from .middleware import ExtraGraphQLDirectiveMiddleware
from .mutation import DjangoSerializerMutation
from .paginations import LimitOffsetGraphqlPagination, PageGraphqlPagination
from .types import (
    DjangoInputObjectType,
    DjangoListObjectType,
    DjangoObjectType,
    DjangoSerializerType,
)

VERSION = (0, 4, 9, "final", "")

__version__ = get_version(VERSION)

__all__ = (
    "__version__",
    # FIELDS
    "DjangoObjectField",
    "DjangoFilterListField",
    "DjangoFilterPaginateListField",
    "DjangoListObjectField",
    # MUTATIONS
    "DjangoSerializerMutation",
    # PAGINATION
    "LimitOffsetGraphqlPagination",
    "PageGraphqlPagination",
    # 'CursorGraphqlPagination',  # Not implemented yet
    # TYPES
    "DjangoObjectType",
    "DjangoListObjectType",
    "DjangoInputObjectType",
    "DjangoSerializerType",
    # DIRECTIVES
    "all_directives",
    "ExtraGraphQLDirectiveMiddleware",
)
