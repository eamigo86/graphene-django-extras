# -*- coding: utf-8 -*-
"""Base classes for GraphQL directives."""
from graphene.utils.str_converters import to_snake_case
from graphql import DirectiveLocation, GraphQLDirective

from ..registry import get_global_registry


class BaseExtraGraphQLDirective(GraphQLDirective):
    """Base class for custom GraphQL directives."""

    def __init__(self):
        """Initialize the directive with registry and configuration."""
        registry = get_global_registry()
        super(BaseExtraGraphQLDirective, self).__init__(
            name=self.get_name(),
            description=self.__doc__,
            args=self.get_args(),
            locations=[
                DirectiveLocation.FIELD,
                DirectiveLocation.FRAGMENT_SPREAD,
                DirectiveLocation.INLINE_FRAGMENT,
            ],
        )
        registry.register_directive(self.get_name(), self)

    @classmethod
    def get_name(cls):
        """Get the directive name from the class name."""
        return to_snake_case(cls.__name__.replace("GraphQLDirective", ""))

    @staticmethod
    def get_args():
        """Get the arguments for the directive."""
        return {}
