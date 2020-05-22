# -*- coding: utf-8 -*-
import random

from graphql import GraphQLArgument, GraphQLNonNull, GraphQLInt

from .base import BaseExtraGraphQLDirective

__all__ = ("ShuffleGraphQLDirective", "SampleGraphQLDirective")


class ShuffleGraphQLDirective(BaseExtraGraphQLDirective):
    """
    Shuffle the list in place
    """

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        if value:
            random.shuffle(value)

        return value


class SampleGraphQLDirective(BaseExtraGraphQLDirective):
    @staticmethod
    def get_args():
        return {
            "k": GraphQLArgument(
                type_=GraphQLNonNull(GraphQLInt), description="Value to default to"
            )
        }

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        k_argument = [arg for arg in directive.arguments if arg.name.value == "k"][0]
        k = int(k_argument.value.value)
        return random.sample(value, k) if value else value
