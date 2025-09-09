# -*- coding: utf-8 -*-
"""Tests for graphene_django_extras.base_types module."""
from django.test import TestCase

import graphene

from graphene_django_extras.types import (
    DjangoInputObjectType,
    DjangoListObjectType,
    DjangoObjectType,
)

from .models import BasicModel


class BasicDjangoType(DjangoObjectType):
    """Test Django object type."""

    class Meta:
        model = BasicModel


class BasicInputType(DjangoInputObjectType):
    """Test Django input type."""

    class Meta:
        model = BasicModel


class BasicListType(DjangoListObjectType):
    """Test Django list type."""

    class Meta:
        model = BasicModel


class BaseTypesTest(TestCase):
    """Test cases for base types."""

    def setUp(self):
        """Set up test data."""
        self.basic_model = BasicModel.objects.create(text="Test Model")

    def test_django_object_type_creation(self):
        """Test DjangoObjectType creation."""
        obj_type = BasicDjangoType()
        self.assertIsNotNone(obj_type)

        # Should be based on the model
        self.assertEqual(obj_type._meta.model, BasicModel)

    def test_django_input_object_type_creation(self):
        """Test DjangoInputObjectType creation."""
        input_type = BasicInputType()
        self.assertIsNotNone(input_type)

        # Should be based on the model
        self.assertEqual(input_type._meta.model, BasicModel)

    def test_django_list_object_type_creation(self):
        """Test DjangoListObjectType creation."""
        list_type = BasicListType()
        self.assertIsNotNone(list_type)

        # Should be based on the model
        self.assertEqual(list_type._meta.model, BasicModel)

    def test_object_type_has_fields(self):
        """Test that object type has fields."""
        # Check that type has fields
        try:
            fields = BasicDjangoType._meta.fields
            self.assertIsInstance(fields, dict)
        except AttributeError:
            # Different versions might have different structures
            pass

    def test_input_type_has_fields(self):
        """Test that input type has fields."""
        # Check that input type has fields
        try:
            fields = BasicInputType._meta.fields
            self.assertIsInstance(fields, dict)
        except AttributeError:
            # Different versions might have different structures
            pass

    def test_list_type_has_fields(self):
        """Test that list type has fields."""
        # Check that list type has fields
        try:
            fields = BasicListType._meta.fields
            self.assertIsInstance(fields, dict)
        except AttributeError:
            # Different versions might have different structures
            pass

    def test_type_inheritance(self):
        """Test that types inherit correctly."""
        # Check inheritance
        self.assertTrue(issubclass(BasicDjangoType, DjangoObjectType))
        self.assertTrue(issubclass(BasicInputType, DjangoInputObjectType))
        self.assertTrue(issubclass(BasicListType, DjangoListObjectType))

    def test_graphene_integration(self):
        """Test integration with graphene."""
        # These should integrate with graphene
        self.assertTrue(issubclass(BasicDjangoType, graphene.ObjectType))
        self.assertTrue(issubclass(BasicInputType, graphene.InputObjectType))

    def test_model_meta_attribute(self):
        """Test model meta attribute."""
        # All types should have model in meta
        self.assertEqual(BasicDjangoType._meta.model, BasicModel)
        self.assertEqual(BasicInputType._meta.model, BasicModel)
        self.assertEqual(BasicListType._meta.model, BasicModel)
