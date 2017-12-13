# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
# from graphql.execution.executor import execute, subscribe
from rest_framework.decorators import (
    authentication_classes, permission_classes, api_view, throttle_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.settings import api_settings
from rest_framework.views import APIView
# from graphql.utils.get_operation_ast import get_operation_ast

from .settings import graphql_api_settings
from .utils import clean_dict


class ExtraGraphQLView(GraphQLView, APIView):
    """
    def execute(self, *args, **kwargs):
        operation_ast = get_operation_ast(args[0])

        if operation_ast and operation_ast.operation == 'subscription':
            return subscribe(self.schema, *args, **kwargs)

        return execute(self.schema, *args, **kwargs)
    """

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(ExtraGraphQLView, cls).as_view(*args, **kwargs)
        view = csrf_exempt(view)
        return view

    def get_response(self, request, data, show_graphiql=False):
        query, variables, operation_name, id = self.get_graphql_params(
            request, data)

        execution_result = self.execute_graphql_request(
            request,
            data,
            query,
            variables,
            operation_name,
            show_graphiql
        )

        status_code = 200
        if execution_result:
            response = {}

            if execution_result.errors:
                response['errors'] = [self.format_error(
                    e) for e in execution_result.errors]

            if execution_result.invalid:
                status_code = 400
            else:
                response['data'] = execution_result.data

            if self.batch:
                response['id'] = id
                response['status'] = status_code

            if graphql_api_settings.CLEAN_RESPONSE and \
                    not query.startswith('\n  query IntrospectionQuery'):
                if response.get('data', None):
                    response['data'] = clean_dict(response['data'])

            result = self.response_json_encode(
                request, response, pretty=show_graphiql)
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
        view = authentication_classes(
            api_settings.DEFAULT_AUTHENTICATION_CLASSES)(view)
        view = throttle_classes(api_settings.DEFAULT_THROTTLE_CLASSES)(view)
        view = api_view(['GET', 'POST'])(view)
        view = csrf_exempt(view)

        return view
