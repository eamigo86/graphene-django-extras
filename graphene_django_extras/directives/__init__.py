# -*- coding: utf-8 -*-
from graphql.type.directives import specified_directives as default_directives

from .list import *
from .numbers import *
from .string import *
try:
    import dateutil
    from .date import *

    date_directives = (DateGraphQLDirective,)
    DATEUTIL_INSTALLED = True
except ImportError:
    date_directives = ()
    DATEUTIL_INSTALLED = False


list_directives = (
    ShuffleGraphQLDirective,
    SampleGraphQLDirective
)
numbers_directives = (
    FloorGraphQLDirective,
    CeilGraphQLDirective
)
string_directives = (
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
    ReplaceGraphQLDirective
)

all_directives = date_directives + list_directives + \
    numbers_directives + string_directives


all_directives = [d() for d in all_directives] + default_directives
