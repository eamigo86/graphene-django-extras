# -*- coding: utf-8 -*-
import hashlib

from django.core.cache import caches
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from graphql import Source, parse, execute
from graphql.execution.executor import subscribe
from graphql.utils.get_operation_ast import get_operation_ast
from rest_framework.decorators import (
    authentication_classes,
    permission_classes,
    api_view,
    throttle_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rx import Observable

from .settings import graphql_api_settings
from .utils import clean_dict


class ExtraGraphQLView(GraphQLView, APIView):
    def get_operation_ast(self, request):
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
        """ Returns a hashed cache key. """
        m = hashlib.md5()
        m.update(request.body)

        return m.hexdigest()

    def super_call(self, request, *args, **kwargs):
        response = super(ExtraGraphQLView, self).dispatch(request, *args, **kwargs)

        return response

    def dispatch(self, request, *args, **kwargs):
        """ Fetches queried data from graphql and returns cached & hashed key. """
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
        operation_ast = get_operation_ast(args[0])

        if operation_ast and operation_ast.operation == "subscription":
            result = subscribe(self.schema, *args, **kwargs)
            if isinstance(result, Observable):
                a = []
                result.subscribe(lambda x: a.append(x))
                if len(a) > 0:
                    result = a[-1]
            return result

        return execute(self.schema, *args, **kwargs)

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(ExtraGraphQLView, cls).as_view(*args, **kwargs)
        view = csrf_exempt(view)
        return view

    def get_response(self, request, data, show_graphiql=False):
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

            if execution_result.invalid:
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
        return self.json_encode(request, response, pretty)


class AuthenticatedGraphQLView(ExtraGraphQLView):
    """
        Extra Graphql view that use 'permission', 'authorization' and 'throttle' classes based on the DRF settings.
        Thanks to @jacobh in (https://github.com/graphql-python/graphene/issues/249#issuecomment-300068390)
    """

    def parse_body(self, request):
        if isinstance(request, Request):
            return request.data
        return super(AuthenticatedGraphQLView, self).parse_body(request)

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(AuthenticatedGraphQLView, cls).as_view(*args, **kwargs)
        view = permission_classes((IsAuthenticated,))(view)
        view = authentication_classes(api_settings.DEFAULT_AUTHENTICATION_CLASSES)(view)
        view = throttle_classes(api_settings.DEFAULT_THROTTLE_CLASSES)(view)
        view = api_view(["GET", "POST"])(view)
        view = csrf_exempt(view)

        return view
