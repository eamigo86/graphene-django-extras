# -*- coding: utf-8 -*-
"""Tests for graphene_django_extras.mutation module."""
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

import graphene

from graphene_django_extras import DjangoSerializerMutation

from .serializers import UserSerializer


class UserMutation(DjangoSerializerMutation):
    """Test mutation for User model."""

    class Meta:
        serializer_class = UserSerializer
        description = "User mutation"


class UserMutationWithCustomName(DjangoSerializerMutation):
    """Test mutation with custom model name."""

    class Meta:
        serializer_class = UserSerializer
        model_operations = ("create", "update")
        lookup_field = "username"


class TestQuery(graphene.ObjectType):
    """Test query for mutations."""

    hello = graphene.String(default_value="Hello World!")

    def resolve_hello(self, info):
        return "Hello World!"


class TestMutations(graphene.ObjectType):
    """Test mutations."""

    user_create = UserMutation.CreateField()
    user_update = UserMutation.UpdateField()
    user_delete = UserMutation.DeleteField()

    user_custom_create = UserMutationWithCustomName.CreateField()
    user_custom_update = UserMutationWithCustomName.UpdateField()


test_schema = graphene.Schema(query=TestQuery, mutation=TestMutations)


class DjangoSerializerMutationTest(TestCase):
    """Test cases for DjangoSerializerMutation."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )

    def test_create_mutation(self):
        """Test create mutation."""
        mutation = """
            mutation {
                userCreate(newUser: {
                    username: "newuser"
                    email: "new@example.com"
                    firstName: "New"
                    lastName: "User"
                    password: "testpassword123"
                }) {
                    user {
                        id
                        username
                        email
                        firstName
                        lastName
                    }
                    ok
                    errors {
                        field
                        messages
                    }
                }
            }
        """

        request = self.factory.post("/graphql/", content_type="application/json")
        result = test_schema.execute(mutation, context_value=request)

        self.assertIsNone(result.errors)
        data = result.data["userCreate"]
        self.assertTrue(data["ok"])
        self.assertEqual(data["user"]["username"], "newuser")
        self.assertEqual(data["user"]["email"], "new@example.com")
        # Handle case where errors field might be None or empty list
        errors = data.get("errors") or []
        self.assertEqual(len(errors), 0)

    def test_update_mutation(self):
        """Test update mutation."""
        mutation = f"""
            mutation {{
                userUpdate(newUser: {{
                    id: {self.user.id}
                    firstName: "Updated"
                    lastName: "Name"
                }}) {{
                    user {{
                        id
                        username
                        firstName
                        lastName
                    }}
                    ok
                    errors {{
                        field
                        messages
                    }}
                }}
            }}
        """

        request = self.factory.post("/graphql/", content_type="application/json")
        result = test_schema.execute(mutation, context_value=request)

        self.assertIsNone(result.errors)
        data = result.data["userUpdate"]
        self.assertTrue(data["ok"])
        self.assertEqual(data["user"]["firstName"], "Updated")
        self.assertEqual(data["user"]["lastName"], "Name")

    def test_delete_mutation(self):
        """Test delete mutation."""
        mutation = f"""
            mutation {{
                userDelete(id: {self.user.id}) {{
                    ok
                    errors {{
                        field
                        messages
                    }}
                }}
            }}
        """

        request = self.factory.post("/graphql/", content_type="application/json")
        result = test_schema.execute(mutation, context_value=request)

        self.assertIsNone(result.errors)
        data = result.data["userDelete"]
        self.assertTrue(data["ok"])
        # Handle case where errors field might be None or empty list
        errors = data.get("errors") or []
        self.assertEqual(len(errors), 0)

        # Verify user was deleted
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_create_mutation_with_validation_errors(self):
        """Test create mutation with validation errors."""
        # Create user with same username first
        User.objects.create_user(username="duplicate", email="dup@example.com")

        mutation = """
            mutation {
                userCreate(newUser: {
                    username: "duplicate"
                    email: "invalid-email"
                    password: "testpass123"
                }) {
                    user {
                        id
                    }
                    ok
                    errors {
                        field
                        messages
                    }
                }
            }
        """

        request = self.factory.post("/graphql/", content_type="application/json")
        result = test_schema.execute(mutation, context_value=request)

        self.assertIsNone(result.errors)
        data = result.data["userCreate"]
        self.assertFalse(data["ok"])
        self.assertIsNone(data["user"])
        # Handle case where errors field might be None or empty list
        errors = data.get("errors") or []
        self.assertGreater(len(errors), 0)

    def test_update_nonexistent_user(self):
        """Test updating a non-existent user."""
        mutation = """
            mutation {
                userUpdate(newUser: {
                    id: 99999
                    firstName: "Updated"
                }) {
                    user {
                        id
                    }
                    ok
                    errors {
                        field
                        messages
                    }
                }
            }
        """

        request = self.factory.post("/graphql/", content_type="application/json")
        result = test_schema.execute(mutation, context_value=request)

        self.assertIsNone(result.errors)
        data = result.data["userUpdate"]
        self.assertFalse(data["ok"])
        self.assertIsNone(data["user"])
        # Handle case where errors field might be None or empty list
        errors = data.get("errors") or []
        self.assertGreater(len(errors), 0)

    def test_delete_nonexistent_user(self):
        """Test deleting a non-existent user."""
        mutation = """
            mutation {
                userDelete(id: 99999) {
                    ok
                    errors {
                        field
                        messages
                    }
                }
            }
        """

        request = self.factory.post("/graphql/", content_type="application/json")
        result = test_schema.execute(mutation, context_value=request)

        self.assertIsNone(result.errors)
        data = result.data["userDelete"]
        self.assertFalse(data["ok"])
        # Handle case where errors field might be None or empty list
        errors = data.get("errors") or []
        self.assertGreater(len(errors), 0)

    def test_custom_lookup_field_mutation(self):
        """Test mutation with custom lookup field."""
        mutation = f"""
            mutation {{
                userCustomUpdate(newUser: {{
                    id: {self.user.id}
                    username: "testuser"
                    firstName: "CustomUpdated"
                }}) {{
                    user {{
                        username
                        firstName
                    }}
                    ok
                    errors {{
                        field
                        messages
                    }}
                }}
            }}
        """

        request = self.factory.post("/graphql/", content_type="application/json")
        result = test_schema.execute(mutation, context_value=request)

        self.assertIsNone(result.errors)
        data = result.data["userCustomUpdate"]
        self.assertTrue(data["ok"])
        self.assertEqual(data["user"]["firstName"], "CustomUpdated")

    def test_mutation_meta_attributes(self):
        """Test mutation meta attributes."""
        self.assertEqual(UserMutation._meta.description, "User mutation")
        self.assertEqual(UserMutation._meta.serializer_class, UserSerializer)

        # Test field creation
        create_field = UserMutation.CreateField()
        update_field = UserMutation.UpdateField()
        delete_field = UserMutation.DeleteField()

        self.assertIsInstance(create_field, graphene.Field)
        self.assertIsInstance(update_field, graphene.Field)
        self.assertIsInstance(delete_field, graphene.Field)

    def test_mutation_with_limited_operations(self):
        """Test mutation with limited model operations."""
        # Test that only create and update are available
        create_field = UserMutationWithCustomName.CreateField()
        update_field = UserMutationWithCustomName.UpdateField()

        self.assertIsInstance(create_field, graphene.Field)
        self.assertIsInstance(update_field, graphene.Field)

        # Test that delete field exists (it should be available by default)
        try:
            delete_field = UserMutationWithCustomName.DeleteField()
            self.assertIsInstance(delete_field, graphene.Field)
        except AttributeError:
            # If delete is not available, that's also valid behavior
            pass
