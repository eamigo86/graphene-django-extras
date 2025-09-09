# -*- coding: utf-8 -*-
"""GraphQL directives for data transformation and formatting."""
from graphql.type.directives import specified_directives as default_directives

from .date import DateGraphQLDirective
from .list import SampleGraphQLDirective, ShuffleGraphQLDirective
from .numbers import CeilGraphQLDirective, FloorGraphQLDirective
from .string import (
    Base64GraphQLDirective,
    CamelCaseGraphQLDirective,
    CapitalizeGraphQLDirective,
    CenterGraphQLDirective,
    CurrencyGraphQLDirective,
    DefaultGraphQLDirective,
    KebabCaseGraphQLDirective,
    LowercaseGraphQLDirective,
    NumberGraphQLDirective,
    ReplaceGraphQLDirective,
    SnakeCaseGraphQLDirective,
    StripGraphQLDirective,
    SwapCaseGraphQLDirective,
    TitleCaseGraphQLDirective,
    UppercaseGraphQLDirective,
)

all_directives = (
    # date
    DateGraphQLDirective,
    # list
    ShuffleGraphQLDirective,
    SampleGraphQLDirective,
    # numbers
    FloorGraphQLDirective,
    CeilGraphQLDirective,
    # string
    DefaultGraphQLDirective,
    Base64GraphQLDirective,
    NumberGraphQLDirective,
    CurrencyGraphQLDirective,
    LowercaseGraphQLDirective,
    UppercaseGraphQLDirective,
    CapitalizeGraphQLDirective,
    CamelCaseGraphQLDirective,
    SnakeCaseGraphQLDirective,
    KebabCaseGraphQLDirective,
    SwapCaseGraphQLDirective,
    StripGraphQLDirective,
    TitleCaseGraphQLDirective,
    CenterGraphQLDirective,
    ReplaceGraphQLDirective,
)


all_directives = [d() for d in all_directives] + [*default_directives]
