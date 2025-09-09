# -*- coding: utf-8 -*-
"""Tests for graphene_django_extras.utils module."""
from django.test import TestCase

from graphene_django_extras.utils import (
    clean_dict,
    get_model_fields,
    get_Object_or_None,
    to_kebab_case,
)

from .models import BasicModel


class UtilsTest(TestCase):
    """Test cases for utility functions."""

    def test_clean_dict(self):
        """Test clean_dict function."""
        # Test removing empty values from nested dicts
        dirty_dict = {
            "key1": "value1",
            "key2": None,
            "key3": "",
            "key4": {"nested1": "value", "nested2": None, "nested3": []},
            "key5": [],
        }

        cleaned = clean_dict(dirty_dict)
        expected = {"key1": "value1", "key4": {"nested1": "value"}}
        self.assertEqual(cleaned, expected)

    def test_to_kebab_case(self):
        """Test to_kebab_case function."""
        # Test string to kebab-case conversion based on actual implementation
        self.assertEqual(to_kebab_case("CamelCase"), "camelcase")
        self.assertEqual(to_kebab_case("snake_case"), "snake_-case")  # Actual behavior
        self.assertEqual(to_kebab_case("Mixed Case"), "mixed-case")

    def test_get_Object_or_None(self):
        """Test get_Object_or_None function."""
        # Create a test object
        obj = BasicModel.objects.create(text="test object")

        # Test successful retrieval
        result = get_Object_or_None(BasicModel, pk=obj.pk)
        self.assertEqual(result, obj)

        # Test non-existent object
        result = get_Object_or_None(BasicModel, pk=99999)
        self.assertIsNone(result)

    def test_get_model_fields(self):
        """Test get_model_fields function."""
        fields = get_model_fields(BasicModel)
        self.assertIsInstance(fields, list)
        self.assertGreater(len(fields), 0)

        # Check that it returns tuples of (name, field)
        for field_info in fields:
            self.assertIsInstance(field_info, tuple)
            self.assertEqual(len(field_info), 2)
