# -*- coding: utf-8 -*-
"""Settings configuration for graphene-django-extras.

This module provides configuration management for the graphene-django-extras
package, including pagination, caching, and other global settings.
"""
from django.conf import settings
from django.test.signals import setting_changed

from rest_framework.settings import APISettings

DEFAULTS = {
    # Pagination
    "DEFAULT_PAGINATION_CLASS": None,  # 'graphene_django_extras.paginations.LimitOffsetGraphqlPagination'
    "DEFAULT_PAGE_SIZE": None,
    "MAX_PAGE_SIZE": None,
    "CLEAN_RESPONSE": False,
    "CACHE_ACTIVE": False,
    "CACHE_TIMEOUT": 300,  # seconds (default 5 min)
}


# List of settings that may be in string import notation.
IMPORT_STRINGS = ("DEFAULT_PAGINATION_CLASS",)


class GraphQLAPISettings(APISettings):
    """API settings class for graphene-django-extras configuration."""

    MODULE_DOC = "https://github.com/eamigo86/graphene-django-extras"

    @property
    def user_settings(self):
        """Get user settings from Django settings."""
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "GRAPHENE_DJANGO_EXTRAS", {})
        return self._user_settings


graphql_api_settings = GraphQLAPISettings(None, DEFAULTS, IMPORT_STRINGS)


def reload_graphql_api_settings(*args, **kwargs):
    """Reload GraphQL API settings when Django settings change."""
    global graphql_api_settings
    setting, value = kwargs["setting"], kwargs["value"]
    if setting == "GRAPHENE_DJANGO_EXTRAS":
        graphql_api_settings = GraphQLAPISettings(value, DEFAULTS, IMPORT_STRINGS)


setting_changed.connect(reload_graphql_api_settings)
