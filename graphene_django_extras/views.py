# -*- coding: utf-8 -*-
"""Enhanced GraphQL views with caching and authentication."""
import hashlib
from typing import TYPE_CHECKING, Any, Callable

from django.core.cache import caches
from django.views.decorators.csrf import csrf_exempt

from graphene_django.views import GraphQLView
from graphql import Source, execute, parse

if TYPE_CHECKING:
    from graphql.execution import subscribe
    from graphql.utilities import get_operation_ast

    try:
        from rx import Observable
    except ImportError:
        Observable = None
else:
    # Import GraphQL functions with version compatibility at runtime
    subscribe: Callable[..., Any]
    get_operation_ast: Callable[..., Any]

    # Try to import subscribe from various locations
    try:
        from graphql.execution import subscribe
    except ImportError:
        try:
            from graphql.execution.executor import subscribe
        except ImportError:
            # For versions without subscribe, provide a placeholder
            def subscribe(*args, **kwargs):
                """Provide placeholder subscribe function when graphql.execution.subscribe is not available."""
                return None

    # Try to import get_operation_ast from various locations
    try:
        from graphql.utilities import get_operation_ast
    except ImportError:
        try:
            from graphql.utils.get_operation_ast import get_operation_ast
        except ImportError:
            try:
                from graphql.execution.executors.asyncio import get_operation_ast
            except ImportError:
                # Provide a placeholder if none of the above work
                def get_operation_ast(*args, **kwargs):
                    """Provide placeholder get_operation_ast function when not available."""
                    return None


# Import rx Observable if available
try:
    from rx import Observable
except ImportError:
    Observable = None

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    throttle_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from .settings import graphql_api_settings
from .utils import clean_dict


class ExtraGraphQLView(GraphQLView, APIView):
    """Enhanced GraphQL view with caching support."""

    def get_operation_ast(self, request):
        """Get the AST of the GraphQL operation from request."""
        data = self.parse_body(request)
        query = request.GET.get("query") or data.get("query")

        if not query:
            return None

        source = Source(query, name="GraphQL request")

        document_ast = parse(source)
        operation_ast = get_operation_ast(document_ast, None)

        return operation_ast

    @staticmethod
    def fetch_cache_key(request):
        """Return a hashed cache key."""
        m = hashlib.sha256()
        m.update(request.body)

        return m.hexdigest()

    def super_call(self, request, *args, **kwargs):
        """Call the parent dispatch method."""
        response = super(ExtraGraphQLView, self).dispatch(request, *args, **kwargs)

        return response

    def dispatch(self, request, *args, **kwargs):
        """Fetch queried data from GraphQL and return cached response."""
        if not graphql_api_settings.CACHE_ACTIVE:
            return self.super_call(request, *args, **kwargs)

        cache = caches["default"]
        operation_ast = self.get_operation_ast(request)
        if operation_ast and operation_ast.operation == "mutation":
            cache.clear()
            return self.super_call(request, *args, **kwargs)

        cache_key = "_graplql_{}".format(self.fetch_cache_key(request))
        response = cache.get(cache_key)

        if not response:
            response = self.super_call(request, *args, **kwargs)

            # cache key and value
            cache.set(cache_key, response, timeout=graphql_api_settings.CACHE_TIMEOUT)

        return response

    def execute(self, *args, **kwargs):
        """Execute GraphQL query with subscription support."""
        operation_ast = get_operation_ast(args[0])

        if operation_ast and operation_ast.operation == "subscription":
            result = subscribe(self.schema, *args, **kwargs)
            if Observable and isinstance(result, Observable):
                a = []
                result.subscribe(lambda x: a.append(x))
                if len(a) > 0:
                    result = a[-1]
            return result

        return execute(self.schema, *args, **kwargs)

    @classmethod
    def as_view(cls, *args, **kwargs):
        """Create view with CSRF exemption."""
        view = super(ExtraGraphQLView, cls).as_view(*args, **kwargs)
        view = csrf_exempt(view)
        return view

    def get_response(self, request, data, show_graphiql=False):
        """Get GraphQL response with error handling and data cleaning."""
        query, variables, operation_name, id = self.get_graphql_params(request, data)

        execution_result = self.execute_graphql_request(
            request, data, query, variables, operation_name, show_graphiql
        )

        status_code = 200
        if execution_result:
            response = {}

            if execution_result.errors:
                response["errors"] = [
                    self.format_error(e) for e in execution_result.errors
                ]

            # Check for invalid result (compatibility with different graphql versions)
            if hasattr(execution_result, "invalid") and execution_result.invalid:
                status_code = 400
            elif execution_result.errors and not execution_result.data:
                # If there are errors and no data, consider it invalid
                status_code = 400
            else:
                response["data"] = execution_result.data

            if self.batch:
                response["id"] = id
                response["status"] = status_code

            if graphql_api_settings.CLEAN_RESPONSE and not query.startswith(
                "\n  query IntrospectionQuery"
            ):
                if response.get("data", None):
                    response["data"] = clean_dict(response["data"])

            result = self.response_json_encode(request, response, pretty=show_graphiql)
        else:
            result = None

        return result, status_code

    def response_json_encode(self, request, response, pretty):
        """Encode response to JSON."""
        return self.json_encode(request, response, pretty)


class AuthenticatedGraphQLView(ExtraGraphQLView):
    """Extra GraphQL view with permission, authorization and throttle classes.

    Based on DRF settings. Thanks to @jacobh in the graphene project.
    """

    def parse_body(self, request):
        """Parse request body for DRF Request objects."""
        if isinstance(request, Request):
            return request.data
        return super(AuthenticatedGraphQLView, self).parse_body(request)

    @classmethod
    def as_view(cls, *args, **kwargs):
        """Create authenticated view with DRF decorators."""
        view = super(AuthenticatedGraphQLView, cls).as_view(*args, **kwargs)
        view = permission_classes((IsAuthenticated,))(view)
        view = authentication_classes(api_settings.DEFAULT_AUTHENTICATION_CLASSES)(view)
        view = throttle_classes(api_settings.DEFAULT_THROTTLE_CLASSES)(view)
        view = api_view(["GET", "POST"])(view)
        view = csrf_exempt(view)

        return view
