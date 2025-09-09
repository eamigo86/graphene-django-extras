# -*- coding: utf-8 -*-
"""Number manipulation GraphQL directives."""
import math

from graphql import GraphQLString

from .base import BaseExtraGraphQLDirective

__all__ = ("FloorGraphQLDirective", "CeilGraphQLDirective")


class FloorGraphQLDirective(BaseExtraGraphQLDirective):
    """Floor value for both String and Float fields."""

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the floor directive."""
        new_value = math.floor(float(value))
        return str(new_value) if info.return_type == GraphQLString else new_value


class CeilGraphQLDirective(BaseExtraGraphQLDirective):
    """Ceil value for both String and Float fields."""

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the ceil directive."""
        new_value = math.ceil(float(value))
        return str(new_value) if info.return_type == GraphQLString else new_value
