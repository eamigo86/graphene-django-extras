# -*- coding: utf-8 -*-
from graphene_django.views import GraphQLView
from rest_framework.decorators import (authentication_classes, permission_classes, api_view, throttle_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.settings import api_settings
from rest_framework.views import APIView


class AuthenticatedGraphQLView(GraphQLView, APIView):
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
        view = api_view(['GET', 'POST'])(view)

        return view
