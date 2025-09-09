# -*- coding: utf-8 -*-
"""String manipulation GraphQL directives."""
import base64

import six
from graphene.utils.str_converters import to_camel_case, to_snake_case
from graphql import GraphQLArgument, GraphQLInt, GraphQLNonNull, GraphQLString

from ..utils import to_kebab_case
from .base import BaseExtraGraphQLDirective

__all__ = (
    "DefaultGraphQLDirective",
    "Base64GraphQLDirective",
    "NumberGraphQLDirective",
    "CurrencyGraphQLDirective",
    "LowercaseGraphQLDirective",
    "UppercaseGraphQLDirective",
    "CapitalizeGraphQLDirective",
    "CamelCaseGraphQLDirective",
    "SnakeCaseGraphQLDirective",
    "KebabCaseGraphQLDirective",
    "SwapCaseGraphQLDirective",
    "StripGraphQLDirective",
    "TitleCaseGraphQLDirective",
    "CenterGraphQLDirective",
    "ReplaceGraphQLDirective",
)


class DefaultGraphQLDirective(BaseExtraGraphQLDirective):
    """Default to given value if None or empty string."""

    @staticmethod
    def get_args():
        """Get arguments for the default directive."""
        return {
            "to": GraphQLArgument(
                GraphQLNonNull(GraphQLString), description="Value to default to"
            )
        }

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the default directive value."""
        if not value:
            to_argument = [
                arg for arg in directive.arguments if arg.name.value == "to"
            ][0]
            return to_argument.value.value

        return value


class Base64GraphQLDirective(BaseExtraGraphQLDirective):
    """Base64 encode or decode string values."""

    @staticmethod
    def get_args():
        """Get arguments for the base64 directive."""
        return {
            "op": GraphQLArgument(
                GraphQLString, description='Action to perform: "encode" or "decode"'
            )
        }

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the base64 directive."""
        if not value:
            return None

        op_argument = [arg for arg in directive.arguments if arg.name.value == "op"]
        op_argument = op_argument[0] if len(op_argument) > 0 else "encode"

        if op_argument in ("decode", "encode"):
            if op_argument == "decode":
                value = base64.urlsafe_b64decode(str(value).encode("ascii"))
            if op_argument == "encode":
                value = base64.urlsafe_b64encode(str(value).encode("ascii"))
            value = value.decode("ascii") if six.PY3 else value

        return value


class NumberGraphQLDirective(BaseExtraGraphQLDirective):
    """String formatting like a specified Python number formatting."""

    @staticmethod
    def get_args():
        """Get arguments for the number directive."""
        return {
            "as": GraphQLArgument(
                GraphQLNonNull(GraphQLString), description="Value to default to"
            )
        }

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the number formatting directive."""
        as_argument = [arg for arg in directive.arguments if arg.name.value == "as"][0]
        return format(float(value or 0), as_argument.value.value)


class CurrencyGraphQLDirective(BaseExtraGraphQLDirective):
    """Format numeric values as currency."""

    @staticmethod
    def get_args():
        """Get arguments for the currency directive."""
        return {
            "symbol": GraphQLArgument(
                GraphQLString, description="Currency symbol (default: $)"
            )
        }

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the currency formatting directive."""
        symbol_argument = next(
            (arg for arg in directive.arguments if arg.name.value == "symbol"), None
        )
        symbol = symbol_argument.value.value if symbol_argument else "$"
        # '${:,.2f}'.format(1234.5)
        return symbol + format(float(value or 0), ",.2f")


class LowercaseGraphQLDirective(BaseExtraGraphQLDirective):
    """Convert string to lowercase."""

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the lowercase directive."""
        value = value if isinstance(value, six.string_types) else str(value)
        return value.lower()


class UppercaseGraphQLDirective(BaseExtraGraphQLDirective):
    """Convert string to uppercase."""

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the uppercase directive."""
        value = value if isinstance(value, six.string_types) else str(value)
        return value.upper()


class CapitalizeGraphQLDirective(BaseExtraGraphQLDirective):
    """Return a copy of the string with its first character capitalized and the rest lowercased."""

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the capitalize directive."""
        value = value if isinstance(value, six.string_types) else str(value)
        return value.capitalize()


class CamelCaseGraphQLDirective(BaseExtraGraphQLDirective):
    """Convert string to camelCase."""

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the camelCase directive."""
        value = value if isinstance(value, six.string_types) else str(value)
        return to_camel_case(value)


class SnakeCaseGraphQLDirective(BaseExtraGraphQLDirective):
    """Convert string to snake_case."""

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the snake_case directive."""
        value = value if isinstance(value, six.string_types) else str(value)
        return to_snake_case(value.title().replace(" ", ""))


class KebabCaseGraphQLDirective(BaseExtraGraphQLDirective):
    """Convert string to kebab-case."""

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the kebab-case directive."""
        value = value if isinstance(value, six.string_types) else str(value)
        return to_kebab_case(value)


class SwapCaseGraphQLDirective(BaseExtraGraphQLDirective):
    """Return a copy of the string with uppercase characters converted to lowercase and vice versa."""

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the swapcase directive."""
        value = value if isinstance(value, six.string_types) else str(value)
        return value.swapcase()


class StripGraphQLDirective(BaseExtraGraphQLDirective):
    """Return a copy of the string with the leading and trailing characters removed.

    The chars argument is a string specifying the set of characters to be removed.
    If omitted or None, the chars argument defaults to removing whitespace.
    The chars argument is not a prefix or suffix; rather, all combinations of its values are stripped.
    """

    @staticmethod
    def get_args():
        """Get arguments for the strip directive."""
        return {
            "chars": GraphQLArgument(
                GraphQLString,
                description="Value to specify the set of characters to be removed",
            )
        }

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the strip directive."""
        chars_argument = [
            arg for arg in directive.arguments if arg.name.value == "chars"
        ]
        chars_argument = (
            chars_argument[0].value.value if len(chars_argument) > 0 else " "
        )

        value = value if isinstance(value, six.string_types) else str(value)
        return value.strip(chars_argument)


class TitleCaseGraphQLDirective(BaseExtraGraphQLDirective):
    """Return a titlecased version of the string where words start with an uppercase character and the remaining characters are lowercase."""

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the title case directive."""
        value = value if isinstance(value, six.string_types) else str(value)
        return value.title()


class CenterGraphQLDirective(BaseExtraGraphQLDirective):
    """Return centered in a string of length width.

    Padding is done using the specified fillchar.
    The original string is returned if width is less than or equal to len(s).
    """

    @staticmethod
    def get_args():
        """Get arguments for the center directive."""
        return {
            "width": GraphQLArgument(
                GraphQLNonNull(GraphQLInt), description="Value to returned str lenght"
            ),
            "fillchar": GraphQLArgument(
                GraphQLString, description="Value to fill the returned str"
            ),
        }

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the center directive."""
        width_argument = [
            arg for arg in directive.arguments if arg.name.value == "width"
        ]
        width_argument = (
            width_argument[0].value.value if len(width_argument) > 0 else len(value)
        )

        fillchar_argument = [
            arg for arg in directive.arguments if arg.name.value == "fillchar"
        ]
        fillchar_argument = (
            fillchar_argument[0].value.value if len(fillchar_argument) > 0 else " "
        )

        value = value if isinstance(value, six.string_types) else str(value)
        return value.center(int(width_argument), fillchar_argument)


class ReplaceGraphQLDirective(BaseExtraGraphQLDirective):
    """Return a copy of the string with all occurrences of substring old replaced by new.

    If the optional argument count is given, only the first count occurrences are replaced.
    """

    @staticmethod
    def get_args():
        """Get arguments for the replace directive."""
        return {
            "old": GraphQLArgument(
                GraphQLNonNull(GraphQLString),
                description="Value of old character to replace",
            ),
            "new": GraphQLArgument(
                GraphQLNonNull(GraphQLString),
                description="Value of new character to replace",
            ),
            "count": GraphQLArgument(
                GraphQLInt, description="Value to returned str lenght"
            ),
        }

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        """Resolve the replace directive."""
        old_argument = [arg for arg in directive.arguments if arg.name.value == "old"]
        old_argument = old_argument[0].value.value if len(old_argument) > 0 else None

        new_argument = [arg for arg in directive.arguments if arg.name.value == "new"]
        new_argument = new_argument[0].value.value if len(new_argument) > 0 else None

        count_argument = [
            arg for arg in directive.arguments if arg.name.value == "count"
        ]
        count_argument = (
            count_argument[0].value.value if len(count_argument) > 0 else -1
        )

        value = value if isinstance(value, six.string_types) else str(value)
        return value.replace(old_argument, new_argument, int(count_argument))
