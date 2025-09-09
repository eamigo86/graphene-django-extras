# -*- coding: utf-8 -*-
"""GraphQL middleware for processing custom directives."""
from graphql.type.directives import GraphQLIncludeDirective, GraphQLSkipDirective

from .registry import get_global_registry


class ExtraGraphQLDirectiveMiddleware(object):
    """Middleware that processes custom GraphQL directives during execution."""

    def resolve(self, next, root, info, **kwargs):
        """Process field resolution with directive handling."""
        result = next(root, info, **kwargs)
        return self.__process_value(result, root, info, **kwargs)

    def __process_value(self, value, root, info, **kwargs):
        registry = get_global_registry()
        field = info.field_nodes[0]
        if not field.directives:
            return value

        new_value = value
        for directive in field.directives:
            if directive.name.value not in (
                GraphQLIncludeDirective.name,
                GraphQLSkipDirective.name,
            ):
                directive_class = registry.get_directive(directive.name.value)
                new_value = directive_class.resolve(
                    new_value, directive, root, info, **kwargs
                )

        return new_value
