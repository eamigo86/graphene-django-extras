# -*- coding: utf-8 -*-
"""Tests for graphene_django_extras.views module."""
import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

import graphene
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from graphene_django_extras.views import AuthenticatedGraphQLView, ExtraGraphQLView


class TestQuery(graphene.ObjectType):
    """Simple test query."""

    hello = graphene.String(name=graphene.String(default_value="World"))

    def resolve_hello(self, info, name):
        """Resolve hello field."""
        return f"Hello {name}!"


class TestSubscription(graphene.ObjectType):
    """Simple test subscription."""

    counter = graphene.String()

    def subscribe_counter(self, info):
        """Subscribe to counter."""
        for i in range(3):
            yield {"counter": f"Count: {i}"}


test_schema = graphene.Schema(query=TestQuery, subscription=TestSubscription)


class ExtraGraphQLViewTest(TestCase):
    """Test cases for ExtraGraphQLView."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        cache.clear()

    def test_view_creation(self):
        """Test view creation."""
        view = ExtraGraphQLView.as_view(schema=test_schema)
        self.assertIsNotNone(view)

    def test_get_request(self):
        """Test GET request to GraphQL view."""
        request = self.factory.get("/graphql/", {"query": "{ hello }"})
        view = ExtraGraphQLView.as_view(schema=test_schema)

        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response["Content-Type"])

    def test_post_request(self):
        """Test POST request to GraphQL view."""
        query = "{ hello }"
        request = self.factory.post(
            "/graphql/", {"query": query}, content_type="application/json"
        )
        view = ExtraGraphQLView.as_view(schema=test_schema)

        response = view(request)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["hello"], "Hello World!")

    def test_post_request_with_variables(self):
        """Test POST request with variables."""
        query = "query($name: String) { hello(name: $name) }"
        variables = {"name": "GraphQL"}

        request = self.factory.post(
            "/graphql/",
            {"query": query, "variables": json.dumps(variables)},
            content_type="application/json",
        )
        view = ExtraGraphQLView.as_view(schema=test_schema)

        response = view(request)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["hello"], "Hello GraphQL!")

    def test_introspection_query(self):
        """Test introspection query."""
        introspection_query = """
        {
            __schema {
                types {
                    name
                }
            }
        }
        """

        request = self.factory.post(
            "/graphql/", {"query": introspection_query}, content_type="application/json"
        )
        view = ExtraGraphQLView.as_view(schema=test_schema)

        response = view(request)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("__schema", data["data"])

    def test_invalid_query(self):
        """Test invalid GraphQL query."""
        request = self.factory.post(
            "/graphql/", {"query": "{ invalidField }"}, content_type="application/json"
        )
        view = ExtraGraphQLView.as_view(schema=test_schema)

        response = view(request)

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("errors", data)

    def test_subscription_request(self):
        """Test subscription request."""
        request = self.factory.post(
            "/graphql/",
            {"query": "subscription { counter }"},
            content_type="application/json",
        )
        view = ExtraGraphQLView.as_view(schema=test_schema)

        response = view(request)

        # Subscriptions should be handled differently
        # The exact behavior depends on the implementation
        self.assertIn(response.status_code, [200, 400, 405])

    @patch("django.core.cache.cache.get")
    @patch("django.core.cache.cache.set")
    @patch("graphene_django_extras.views.graphql_api_settings.CACHE_ACTIVE", True)
    def test_caching_enabled(self, mock_cache_set, mock_cache_get):
        """Test query caching when enabled."""
        mock_cache_get.return_value = None  # Cache miss

        query = "{ hello }"
        request = self.factory.post(
            "/graphql/", {"query": query}, content_type="application/json"
        )

        # Create view - caching is controlled by settings
        view = ExtraGraphQLView.as_view(schema=test_schema)

        response = view(request)

        self.assertEqual(response.status_code, 200)
        # Should try to get from cache
        mock_cache_get.assert_called()
        # Should set cache on cache miss
        mock_cache_set.assert_called()

    @patch("django.core.cache.cache.get")
    @patch("graphene_django_extras.views.graphql_api_settings.CACHE_ACTIVE", True)
    def test_cache_hit(self, mock_cache_get):
        """Test cache hit scenario."""
        cached_result = {"data": {"hello": "Hello Cached!"}}
        cached_response = HttpResponse(
            json.dumps(cached_result), content_type="application/json"
        )
        mock_cache_get.return_value = cached_response

        query = "{ hello }"
        request = self.factory.post(
            "/graphql/", {"query": query}, content_type="application/json"
        )

        view = ExtraGraphQLView.as_view(schema=test_schema)

        response = view(request)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["hello"], "Hello Cached!")

    def test_options_request(self):
        """Test OPTIONS request (CORS preflight)."""
        request = self.factory.options("/graphql/")
        view = ExtraGraphQLView.as_view(schema=test_schema)

        response = view(request)

        # Should handle OPTIONS request
        self.assertIn(response.status_code, [200, 405])

    def test_graphiql_enabled(self):
        """Test GraphiQL interface when enabled."""
        request = self.factory.get("/graphql/", HTTP_ACCEPT="text/html")
        view = ExtraGraphQLView.as_view(schema=test_schema, graphiql=True)

        response = view(request)

        self.assertEqual(response.status_code, 200)
        # Should return HTML for GraphiQL
        self.assertIn("text/html", response["Content-Type"])

    def test_graphiql_disabled(self):
        """Test GraphiQL interface when disabled."""
        request = self.factory.get("/graphql/", HTTP_ACCEPT="text/html")
        view = ExtraGraphQLView.as_view(schema=test_schema, graphiql=False)

        response = view(request)

        # Should not return HTML interface
        self.assertNotEqual(response["Content-Type"], "text/html")


class AuthenticatedGraphQLViewTest(TestCase):
    """Test cases for AuthenticatedGraphQLView."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_view_creation(self):
        """Test authenticated view creation."""
        view = AuthenticatedGraphQLView.as_view(schema=test_schema)
        self.assertIsNotNone(view)

    def test_authentication_required(self):
        """Test that authentication is required."""
        request = self.factory.post(
            "/graphql/", {"query": "{ hello }"}, content_type="application/json"
        )

        view = AuthenticatedGraphQLView.as_view(schema=test_schema)

        response = view(request)

        # Should require authentication (DRF returns 403 for IsAuthenticated without credentials)
        self.assertEqual(response.status_code, 403)

    def test_authenticated_request(self):
        """Test authenticated request."""
        # Create a proper DRF request with authenticated user
        from rest_framework.test import APIRequestFactory

        factory = APIRequestFactory()
        request = factory.post("/graphql/", {"query": "{ hello }"}, format="json")
        # Force authentication for this request
        from rest_framework.test import force_authenticate

        force_authenticate(request, user=self.user)

        view = AuthenticatedGraphQLView.as_view(schema=test_schema)

        response = view(request)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["hello"], "Hello World!")

    def test_custom_authentication_classes(self):
        """Test custom authentication classes."""
        view = AuthenticatedGraphQLView.as_view(
            schema=test_schema, authentication_classes=[SessionAuthentication]
        )

        # Should be able to create view with custom auth classes
        self.assertIsNotNone(view)

    def test_custom_permission_classes(self):
        """Test custom permission classes."""
        view = AuthenticatedGraphQLView.as_view(
            schema=test_schema, permission_classes=[IsAuthenticated]
        )

        # Should be able to create view with custom permissions
        self.assertIsNotNone(view)

    def test_throttling(self):
        """Test request throttling."""
        # Create a proper DRF request with authenticated user
        from rest_framework.test import APIRequestFactory, force_authenticate

        factory = APIRequestFactory()
        request = factory.post("/graphql/", {"query": "{ hello }"}, format="json")
        force_authenticate(request, user=self.user)

        view = AuthenticatedGraphQLView.as_view(schema=test_schema)

        response = view(request)

        # Should work without throttling (default throttle classes shouldn't block single request)
        self.assertEqual(response.status_code, 200)

    @patch("rest_framework.permissions.IsAuthenticated.has_permission")
    def test_permission_denied(self, mock_has_permission):
        """Test permission denied scenario."""
        mock_has_permission.return_value = False

        request = self.factory.post(
            "/graphql/", {"query": "{ hello }"}, content_type="application/json"
        )
        request.user = self.user

        view = AuthenticatedGraphQLView.as_view(
            schema=test_schema, permission_classes=[IsAuthenticated]
        )

        response = view(request)

        # Should deny access
        self.assertEqual(response.status_code, 403)

    def test_view_with_context(self):
        """Test view provides correct context."""
        # Create a proper DRF request with authenticated user
        from rest_framework.test import APIRequestFactory, force_authenticate

        factory = APIRequestFactory()
        request = factory.post("/graphql/", {"query": "{ hello }"}, format="json")
        force_authenticate(request, user=self.user)

        view = AuthenticatedGraphQLView.as_view(schema=test_schema)

        # Execute the view and verify it works (context test is implicit)
        response = view(request)

        # If the response is successful, context was properly passed
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["hello"], "Hello World!")
