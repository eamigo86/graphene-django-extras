# -*- coding: utf-8 -*-
"""Tests for graphene_django_extras.middleware module."""
from unittest.mock import Mock, patch

from django.test import TestCase

from graphene_django_extras.directives.base import BaseExtraGraphQLDirective
from graphene_django_extras.middleware import ExtraGraphQLDirectiveMiddleware


class MockDirective(BaseExtraGraphQLDirective):
    """Mock directive for testing."""

    @classmethod
    def resolve(cls, value, directive, root, info, **kwargs):
        """Mock directive resolution that adds a prefix."""
        if isinstance(value, str):
            return f"processed_{value}"
        return value


class ExtraGraphQLDirectiveMiddlewareTest(TestCase):
    """Test cases for ExtraGraphQLDirectiveMiddleware."""

    def setUp(self):
        """Set up test cases."""
        self.middleware = ExtraGraphQLDirectiveMiddleware()

    def test_middleware_creation(self):
        """Test middleware creation."""
        self.assertIsInstance(self.middleware, ExtraGraphQLDirectiveMiddleware)
        self.assertTrue(hasattr(self.middleware, "resolve"))

    def test_resolve_without_directives(self):
        """Test resolve method when field has no directives."""
        # Mock the next function
        next_func = Mock(return_value="test_value")

        # Mock info object with no directives
        mock_info = Mock()
        mock_field = Mock()
        mock_field.directives = []
        mock_info.field_nodes = [mock_field]

        result = self.middleware.resolve(next_func, None, mock_info)

        self.assertEqual(result, "test_value")
        next_func.assert_called_once_with(None, mock_info)

    def test_resolve_with_skip_directive(self):
        """Test resolve method with built-in skip directive."""
        # Mock the next function
        next_func = Mock(return_value="test_value")

        # Mock info object with skip directive
        mock_info = Mock()
        mock_field = Mock()
        mock_directive = Mock()
        mock_directive.name.value = "skip"
        mock_field.directives = [mock_directive]
        mock_info.field_nodes = [mock_field]

        result = self.middleware.resolve(next_func, None, mock_info)

        # Should return value without processing since it's a built-in directive
        self.assertEqual(result, "test_value")

    def test_resolve_with_include_directive(self):
        """Test resolve method with built-in include directive."""
        # Mock the next function
        next_func = Mock(return_value="test_value")

        # Mock info object with include directive
        mock_info = Mock()
        mock_field = Mock()
        mock_directive = Mock()
        mock_directive.name.value = "include"
        mock_field.directives = [mock_directive]
        mock_info.field_nodes = [mock_field]

        result = self.middleware.resolve(next_func, None, mock_info)

        # Should return value without processing since it's a built-in directive
        self.assertEqual(result, "test_value")

    @patch("graphene_django_extras.middleware.get_global_registry")
    def test_resolve_with_custom_directive(self, mock_get_registry):
        """Test resolve method with custom directive."""
        # Mock the registry and directive
        mock_registry = Mock()
        mock_registry.get_directive.return_value = MockDirective
        mock_get_registry.return_value = mock_registry

        # Mock the next function
        next_func = Mock(return_value="test_value")

        # Mock info object with custom directive
        mock_info = Mock()
        mock_field = Mock()
        mock_directive = Mock()
        mock_directive.name.value = "custom_directive"
        mock_field.directives = [mock_directive]
        mock_info.field_nodes = [mock_field]

        result = self.middleware.resolve(next_func, None, mock_info)

        # Should process the value through the custom directive
        self.assertEqual(result, "processed_test_value")
        mock_registry.get_directive.assert_called_once_with("custom_directive")

    @patch("graphene_django_extras.middleware.get_global_registry")
    def test_resolve_with_multiple_custom_directives(self, mock_get_registry):
        """Test resolve method with multiple custom directives."""
        # Mock the registry and directive
        mock_registry = Mock()
        mock_registry.get_directive.return_value = MockDirective
        mock_get_registry.return_value = mock_registry

        # Mock the next function
        next_func = Mock(return_value="value")

        # Mock info object with multiple custom directives
        mock_info = Mock()
        mock_field = Mock()

        # Create multiple directives
        mock_directive1 = Mock()
        mock_directive1.name.value = "directive1"
        mock_directive2 = Mock()
        mock_directive2.name.value = "directive2"

        mock_field.directives = [mock_directive1, mock_directive2]
        mock_info.field_nodes = [mock_field]

        result = self.middleware.resolve(next_func, None, mock_info)

        # Should process the value through both directives
        self.assertEqual(result, "processed_processed_value")
        self.assertEqual(mock_registry.get_directive.call_count, 2)

    @patch("graphene_django_extras.middleware.get_global_registry")
    def test_resolve_with_mixed_directives(self, mock_get_registry):
        """Test resolve method with both built-in and custom directives."""
        # Mock the registry and directive
        mock_registry = Mock()
        mock_registry.get_directive.return_value = MockDirective
        mock_get_registry.return_value = mock_registry

        # Mock the next function
        next_func = Mock(return_value="value")

        # Mock info object with mixed directives
        mock_info = Mock()
        mock_field = Mock()

        # Create mixed directives (built-in and custom)
        mock_skip_directive = Mock()
        mock_skip_directive.name.value = "skip"
        mock_custom_directive = Mock()
        mock_custom_directive.name.value = "custom"

        mock_field.directives = [mock_skip_directive, mock_custom_directive]
        mock_info.field_nodes = [mock_field]

        result = self.middleware.resolve(next_func, None, mock_info)

        # Should only process custom directive, skip the built-in one
        self.assertEqual(result, "processed_value")
        mock_registry.get_directive.assert_called_once_with("custom")

    def test_process_value_method_directly(self):
        """Test the private __process_value method behavior."""
        # This tests the internal method by calling resolve which uses it
        next_func = Mock(return_value="test")

        # Mock info with no directives
        mock_info = Mock()
        mock_field = Mock()
        mock_field.directives = []
        mock_info.field_nodes = [mock_field]

        result = self.middleware.resolve(next_func, None, mock_info)
        self.assertEqual(result, "test")

    @patch("graphene_django_extras.middleware.get_global_registry")
    def test_directive_error_handling(self, mock_get_registry):
        """Test error handling when directive processing fails."""
        # Mock a registry that raises an exception
        mock_registry = Mock()
        mock_registry.get_directive.side_effect = Exception("Directive not found")
        mock_get_registry.return_value = mock_registry

        next_func = Mock(return_value="value")

        # Mock info object with custom directive
        mock_info = Mock()
        mock_field = Mock()
        mock_directive = Mock()
        mock_directive.name.value = "bad_directive"
        mock_field.directives = [mock_directive]
        mock_info.field_nodes = [mock_field]

        # Should raise the exception from the registry
        with self.assertRaises(Exception):
            self.middleware.resolve(next_func, None, mock_info)

    @patch("graphene_django_extras.middleware.get_global_registry")
    def test_directive_with_non_string_value(self, mock_get_registry):
        """Test directive processing with non-string values."""
        # Mock the registry and directive
        mock_registry = Mock()
        mock_registry.get_directive.return_value = MockDirective
        mock_get_registry.return_value = mock_registry

        # Mock the next function returning a non-string value
        next_func = Mock(return_value=42)

        # Mock info object with custom directive
        mock_info = Mock()
        mock_field = Mock()
        mock_directive = Mock()
        mock_directive.name.value = "custom"
        mock_field.directives = [mock_directive]
        mock_info.field_nodes = [mock_field]

        result = self.middleware.resolve(next_func, None, mock_info)

        # MockDirective should return the value unchanged for non-strings
        self.assertEqual(result, 42)

    def test_middleware_with_kwargs(self):
        """Test middleware passing through keyword arguments."""
        next_func = Mock(return_value="value")

        # Mock info with no directives
        mock_info = Mock()
        mock_field = Mock()
        mock_field.directives = []
        mock_info.field_nodes = [mock_field]

        result = self.middleware.resolve(next_func, None, mock_info, custom_arg="test")

        self.assertEqual(result, "value")
        next_func.assert_called_once_with(None, mock_info, custom_arg="test")

    @patch("graphene_django_extras.middleware.get_global_registry")
    def test_directive_receives_kwargs(self, mock_get_registry):
        """Test that directives receive keyword arguments."""

        # Create a mock directive that captures its arguments
        class KwargsCapturingDirective(BaseExtraGraphQLDirective):
            captured_kwargs = None

            @classmethod
            def resolve(cls, value, directive, root, info, **kwargs):
                cls.captured_kwargs = kwargs
                return value

        mock_registry = Mock()
        mock_registry.get_directive.return_value = KwargsCapturingDirective
        mock_get_registry.return_value = mock_registry

        next_func = Mock(return_value="value")

        # Mock info object with custom directive
        mock_info = Mock()
        mock_field = Mock()
        mock_directive = Mock()
        mock_directive.name.value = "kwargs_test"
        mock_field.directives = [mock_directive]
        mock_info.field_nodes = [mock_field]

        self.middleware.resolve(next_func, None, mock_info, test_arg="test_value")

        # Verify the directive received the kwargs
        self.assertEqual(
            KwargsCapturingDirective.captured_kwargs, {"test_arg": "test_value"}
        )


class MiddlewareIntegrationTest(TestCase):
    """Integration tests for middleware functionality."""

    def setUp(self):
        """Set up integration tests."""
        self.middleware = ExtraGraphQLDirectiveMiddleware()

    @patch("graphene_django_extras.middleware.get_global_registry")
    def test_full_middleware_pipeline(self, mock_get_registry):
        """Test the complete middleware pipeline."""

        # Create a directive that modifies the value
        class PipelineDirective(BaseExtraGraphQLDirective):
            @classmethod
            def resolve(cls, value, directive, root, info, **kwargs):
                return f"pipeline:{value}"

        mock_registry = Mock()
        mock_registry.get_directive.return_value = PipelineDirective
        mock_get_registry.return_value = mock_registry

        # Simulate the GraphQL resolver chain
        def mock_resolver(root, info, **kwargs):
            return "original_value"

        # Mock complete info structure
        mock_info = Mock()
        mock_field = Mock()
        mock_directive = Mock()
        mock_directive.name.value = "pipeline"
        mock_field.directives = [mock_directive]
        mock_info.field_nodes = [mock_field]

        result = self.middleware.resolve(mock_resolver, None, mock_info)

        self.assertEqual(result, "pipeline:original_value")

    def test_middleware_preserves_resolver_context(self):
        """Test that middleware preserves resolver context."""

        def context_aware_resolver(root, info, **kwargs):
            # This resolver uses the context
            return f"root:{root}, context:{info}"

        # Mock info with no directives
        mock_info = Mock()
        mock_field = Mock()
        mock_field.directives = []
        mock_info.field_nodes = [mock_field]

        mock_root = "test_root"

        result = self.middleware.resolve(context_aware_resolver, mock_root, mock_info)

        # Verify that root and info were passed correctly
        expected = f"root:{mock_root}, context:{mock_info}"
        self.assertEqual(result, expected)
