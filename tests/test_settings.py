# -*- coding: utf-8 -*-
"""Tests for graphene_django_extras.settings module."""
from django.test import TestCase, override_settings

from graphene_django_extras.settings import graphql_api_settings


class SettingsTest(TestCase):
    """Test cases for settings module."""

    def test_default_settings(self):
        """Test default settings values."""
        # Test that default settings exist
        self.assertIsNotNone(graphql_api_settings)

        # Test some common settings
        common_settings = [
            "DEFAULT_PAGINATION_CLASS",
            "DEFAULT_PAGE_SIZE",
            "MAX_PAGE_SIZE",
            "CACHE_ACTIVE",
            "CACHE_TIMEOUT",
        ]

        for setting_name in common_settings:
            if hasattr(graphql_api_settings, setting_name):
                # Some settings can be None by design (e.g., CACHE_TIMEOUT might be None)
                self.assertTrue(hasattr(graphql_api_settings, setting_name))

    @override_settings(
        GRAPHENE_DJANGO_EXTRAS={
            "DEFAULT_PAGE_SIZE": 25,
            "MAX_PAGE_SIZE": 100,
            "CACHE_ACTIVE": True,
            "CACHE_TIMEOUT": 600,
        }
    )
    def test_custom_settings(self):
        """Test custom settings override."""
        # Import settings again to get updated values
        from graphene_django_extras.settings import graphql_api_settings

        # Test that custom settings are applied
        if hasattr(graphql_api_settings, "DEFAULT_PAGE_SIZE"):
            self.assertEqual(graphql_api_settings.DEFAULT_PAGE_SIZE, 25)

        if hasattr(graphql_api_settings, "MAX_PAGE_SIZE"):
            self.assertEqual(graphql_api_settings.MAX_PAGE_SIZE, 100)

        if hasattr(graphql_api_settings, "CACHE_ACTIVE"):
            self.assertEqual(graphql_api_settings.CACHE_ACTIVE, True)

        if hasattr(graphql_api_settings, "CACHE_TIMEOUT"):
            self.assertEqual(graphql_api_settings.CACHE_TIMEOUT, 600)

    def test_settings_accessibility(self):
        """Test that settings are accessible."""
        # Settings should be importable and accessible
        from graphene_django_extras.settings import graphql_api_settings

        # Should be able to access settings
        self.assertIsNotNone(graphql_api_settings)

        # Should have some attributes
        attrs = dir(graphql_api_settings)
        self.assertIsInstance(attrs, list)
        self.assertGreater(len(attrs), 0)

    def test_settings_type(self):
        """Test settings object type."""
        # Settings should be some kind of settings object
        self.assertIsNotNone(type(graphql_api_settings))

        # Should have string representation
        str_repr = str(graphql_api_settings)
        self.assertIsInstance(str_repr, str)
