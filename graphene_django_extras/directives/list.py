# -*- coding: utf-8 -*-
"""List manipulation GraphQL directives."""
import random

from graphql import GraphQLArgument, GraphQLInt, GraphQLNonNull

from .base import BaseExtraGraphQLDirective

__all__ = ("ShuffleGraphQLDirective", "SampleGraphQLDirective")


class ShuffleGraphQLDirective(BaseExtraGraphQLDirective):
    """Shuffle the list in place."""

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the shuffle directive."""
        if value:
            random.shuffle(value)

        return value


class SampleGraphQLDirective(BaseExtraGraphQLDirective):
    """Sample k random elements from a list."""

    @staticmethod
    def get_args():
        """Get arguments for the sample directive."""
        return {
            "k": GraphQLArgument(
                GraphQLNonNull(GraphQLInt), description="Value to default to"
            )
        }

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the sample directive."""
        k_argument = [arg for arg in directive.arguments if arg.name.value == "k"][0]
        k = int(k_argument.value.value)
        return random.sample(value, k) if value else value
