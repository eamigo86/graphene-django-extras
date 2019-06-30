# -*- coding: utf-8 -*-
import math

from graphql import GraphQLString

from .base import BaseExtraGraphQLDirective

__all__ = ("FloorGraphQLDirective", "CeilGraphQLDirective")


class FloorGraphQLDirective(BaseExtraGraphQLDirective):
    """
    Floors value. Supports both String and Float fields.
    """

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        new_value = math.floor(float(value))
        return str(new_value) if info.return_type == GraphQLString else new_value


class CeilGraphQLDirective(BaseExtraGraphQLDirective):
    """
    Ceils value. Supports both String and Float fields.
    """

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        new_value = math.ceil(float(value))
        return str(new_value) if info.return_type == GraphQLString else new_value
