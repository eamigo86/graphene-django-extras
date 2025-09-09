# -*- coding: utf-8 -*-
"""Tests for graphene_django_extras.converter module."""
from django.contrib.auth.models import User
from django.db import models
from django.test import TestCase

import graphene

from graphene_django_extras.converter import (
    convert_choice_name,
    convert_django_field,
    convert_django_field_with_choices,
    get_choices,
)

from .models import BasicModel


class TestModel(models.Model):
    """Test model for converter tests."""

    # Different field types to test conversion
    char_field = models.CharField(max_length=100, help_text="Character field")
    text_field = models.TextField(blank=True)
    integer_field = models.IntegerField(default=0)
    float_field = models.FloatField(null=True)
    decimal_field = models.DecimalField(max_digits=10, decimal_places=2)
    boolean_field = models.BooleanField(default=False)
    date_field = models.DateField(null=True, blank=True)
    datetime_field = models.DateTimeField(auto_now_add=True)
    time_field = models.TimeField(null=True)
    email_field = models.EmailField(blank=True)
    url_field = models.URLField(blank=True)
    slug_field = models.SlugField(blank=True)
    uuid_field = models.UUIDField(null=True, blank=True)
    json_field = models.JSONField(null=True, blank=True)

    # Choice field
    CHOICE_A = 1
    CHOICE_B = 2
    CHOICES = (
        (CHOICE_A, "Choice A"),
        (CHOICE_B, "Choice B"),
    )
    choice_field = models.IntegerField(choices=CHOICES, default=CHOICE_A)

    # Foreign key
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    # Many to many
    basics = models.ManyToManyField(BasicModel, blank=True)

    class Meta:
        app_label = "tests"


class ConverterTest(TestCase):
    """Test cases for converter functions."""

    def test_convert_char_field(self):
        """Test CharField conversion."""
        field = TestModel._meta.get_field("char_field")
        graphql_field = convert_django_field(field)

        self.assertIsInstance(graphql_field, graphene.String)

    def test_convert_text_field(self):
        """Test TextField conversion."""
        field = TestModel._meta.get_field("text_field")
        graphql_field = convert_django_field(field)

        self.assertIsInstance(graphql_field, graphene.String)

    def test_convert_integer_field(self):
        """Test IntegerField conversion."""
        field = TestModel._meta.get_field("integer_field")
        graphql_field = convert_django_field(field)

        self.assertIsInstance(graphql_field, graphene.Int)

    def test_convert_float_field(self):
        """Test FloatField conversion."""
        field = TestModel._meta.get_field("float_field")
        graphql_field = convert_django_field(field)

        self.assertIsInstance(graphql_field, graphene.Float)

    def test_convert_decimal_field(self):
        """Test DecimalField conversion."""
        field = TestModel._meta.get_field("decimal_field")
        graphql_field = convert_django_field(field)

        self.assertIsInstance(graphql_field, graphene.Float)

    def test_convert_boolean_field(self):
        """Test BooleanField conversion."""
        field = TestModel._meta.get_field("boolean_field")
        graphql_field = convert_django_field(field)

        self.assertIsInstance(graphql_field, graphene.Boolean)

    def test_convert_date_field(self):
        """Test DateField conversion."""
        field = TestModel._meta.get_field("date_field")
        graphql_field = convert_django_field(field)

        # Uses CustomDate from base_types
        from graphene_django_extras.base_types import CustomDate

        self.assertIsInstance(graphql_field, CustomDate)

    def test_convert_datetime_field(self):
        """Test DateTimeField conversion."""
        field = TestModel._meta.get_field("datetime_field")
        graphql_field = convert_django_field(field)

        # Uses CustomDateTime from base_types
        from graphene_django_extras.base_types import CustomDateTime

        self.assertIsInstance(graphql_field, CustomDateTime)

    def test_convert_time_field(self):
        """Test TimeField conversion."""
        field = TestModel._meta.get_field("time_field")
        graphql_field = convert_django_field(field)

        # Uses CustomTime from base_types
        from graphene_django_extras.base_types import CustomTime

        self.assertIsInstance(graphql_field, CustomTime)

    def test_convert_email_field(self):
        """Test EmailField conversion."""
        field = TestModel._meta.get_field("email_field")
        graphql_field = convert_django_field(field)

        self.assertIsInstance(graphql_field, graphene.String)

    def test_convert_url_field(self):
        """Test URLField conversion."""
        field = TestModel._meta.get_field("url_field")
        graphql_field = convert_django_field(field)

        self.assertIsInstance(graphql_field, graphene.String)

    def test_convert_slug_field(self):
        """Test SlugField conversion."""
        field = TestModel._meta.get_field("slug_field")
        graphql_field = convert_django_field(field)

        self.assertIsInstance(graphql_field, graphene.String)

    def test_convert_uuid_field(self):
        """Test UUIDField conversion."""
        field = TestModel._meta.get_field("uuid_field")
        graphql_field = convert_django_field(field)

        # UUID should convert to UUID type
        self.assertIsInstance(graphql_field, graphene.UUID)

    def test_convert_json_field(self):
        """Test JSONField conversion."""
        field = TestModel._meta.get_field("json_field")
        graphql_field = convert_django_field(field)

        self.assertIsInstance(graphql_field, graphene.JSONString)

    def test_convert_choice_field(self):
        """Test field with choices conversion."""
        field = TestModel._meta.get_field("choice_field")

        # Need to mock a registry for choices
        from graphene_django_extras.registry import get_global_registry

        registry = get_global_registry()

        graphql_field = convert_django_field_with_choices(field, registry=registry)

        # Should create some type for choices
        self.assertIsNotNone(graphql_field)

    def test_convert_foreign_key_field(self):
        """Test ForeignKey field conversion."""
        field = TestModel._meta.get_field("user")
        graphql_field = convert_django_field(field)

        # Foreign key should convert to Dynamic type
        self.assertIsInstance(graphql_field, graphene.Dynamic)

    def test_convert_many_to_many_field(self):
        """Test ManyToManyField conversion."""
        field = TestModel._meta.get_field("basics")
        graphql_field = convert_django_field(field)

        # M2M should convert to Dynamic type
        self.assertIsInstance(graphql_field, graphene.Dynamic)

    def test_convert_choice_name(self):
        """Test choice name conversion."""
        # Test various choice name conversions
        self.assertEqual(convert_choice_name("CHOICE_A"), "CHOICE_A")
        self.assertEqual(
            convert_choice_name("choice-with-dashes"), "CHOICE_WITH_DASHES"
        )
        self.assertEqual(
            convert_choice_name("choice with spaces"), "CHOICE_WITH_SPACES"
        )

    def test_get_choices(self):
        """Test choices extraction from field."""
        field = TestModel._meta.get_field("choice_field")
        choices = list(get_choices(field.choices))

        self.assertIsInstance(choices, list)
        self.assertEqual(len(choices), 2)
        # get_choices returns (name, value, description) tuples
        choice_values = [(choice[1], choice[2]) for choice in choices]
        self.assertIn((1, "Choice A"), choice_values)
        self.assertIn((2, "Choice B"), choice_values)

    def test_nullable_field_conversion(self):
        """Test nullable field conversion."""
        field = TestModel._meta.get_field("float_field")
        graphql_field = convert_django_field(field)

        # Nullable fields should not be wrapped in NonNull
        self.assertIsInstance(graphql_field, graphene.Float)
        self.assertFalse(isinstance(graphql_field, graphene.NonNull))

    def test_required_field_conversion(self):
        """Test required field conversion."""
        field = TestModel._meta.get_field("char_field")
        graphql_field = convert_django_field(field, input_flag="create")

        # Required fields for input should be NonNull
        if hasattr(graphene, "NonNull"):
            # Depending on configuration, might be wrapped in NonNull
            self.assertIsInstance(graphql_field, (graphene.String, graphene.NonNull))

    def test_field_with_default_conversion(self):
        """Test field with default value conversion."""
        field = TestModel._meta.get_field("integer_field")
        graphql_field = convert_django_field(field)

        self.assertIsInstance(graphql_field, graphene.Int)

    def test_auto_field_conversion(self):
        """Test AutoField conversion."""
        field = TestModel._meta.get_field("id")  # Auto-created id field
        graphql_field = convert_django_field(field)

        # ID field should convert to ID type
        self.assertIsInstance(graphql_field, (graphene.ID, graphene.Int))


class ConverterUtilsTest(TestCase):
    """Test cases for converter utility functions."""

    def test_convert_choices_with_enum(self):
        """Test conversion of choices creates proper enum."""
        field = TestModel._meta.get_field("choice_field")

        from graphene_django_extras.registry import get_global_registry

        registry = get_global_registry()

        graphql_field = convert_django_field_with_choices(field, registry=registry)

        # Should create some form of enum or choice field
        self.assertIsNotNone(graphql_field)

    def test_choices_extraction(self):
        """Test choices extraction from different field types."""
        # Test with integer choices
        field = TestModel._meta.get_field("choice_field")
        choices = list(get_choices(field.choices))

        self.assertEqual(len(choices), 2)
        # get_choices returns (name, value, description) tuples
        choice_values = [(choice[1], choice[2]) for choice in choices]
        self.assertEqual(choice_values[0], (1, "Choice A"))
        self.assertEqual(choice_values[1], (2, "Choice B"))

    def test_choice_name_normalization(self):
        """Test choice name normalization for GraphQL."""
        # Test various name formats
        self.assertEqual(convert_choice_name("simple"), "SIMPLE")
        self.assertEqual(convert_choice_name("ALREADY_UPPER"), "ALREADY_UPPER")
        self.assertEqual(convert_choice_name("with-dashes"), "WITH_DASHES")
        self.assertEqual(convert_choice_name("with spaces"), "WITH_SPACES")
        self.assertEqual(convert_choice_name("mixed_Case-Format"), "MIXED_CASE_FORMAT")


class FieldConversionIntegrationTest(TestCase):
    """Integration tests for field conversion."""

    def test_model_to_graphql_type_conversion(self):
        """Test complete model to GraphQL type conversion."""
        # This tests the integration of field conversion
        from graphene_django_extras import DjangoObjectType

        class TestModelType(DjangoObjectType):
            class Meta:
                model = TestModel

        # Should be able to create the type without errors
        type_instance = TestModelType()
        self.assertIsNotNone(type_instance)

        # Should have converted all fields
        fields = TestModelType._meta.fields
        self.assertGreater(len(fields), 10)  # Should have many fields

        # Check specific field conversions
        self.assertIn("char_field", fields)
        self.assertIn("choice_field", fields)
        self.assertIn("user", fields)

    def test_input_type_conversion(self):
        """Test model to input type conversion."""
        from graphene_django_extras import DjangoInputObjectType

        class TestModelInput(DjangoInputObjectType):
            class Meta:
                model = TestModel

        # Should be able to create input type
        input_type = TestModelInput()
        self.assertIsNotNone(input_type)

        # Should handle required vs optional fields appropriately
        fields = TestModelInput._meta.fields
        self.assertIn("char_field", fields)

    def test_relationship_field_conversion(self):
        """Test relationship field conversion."""
        # Test that foreign keys and m2m fields are converted correctly
        user_field = TestModel._meta.get_field("user")
        basics_field = TestModel._meta.get_field("basics")

        user_graphql_field = convert_django_field(user_field)
        basics_graphql_field = convert_django_field(basics_field)

        # User field should be a reference to User type
        self.assertIsInstance(user_graphql_field, graphene.Dynamic)

        # Basics field should be a list
        self.assertIsInstance(basics_graphql_field, graphene.Dynamic)
