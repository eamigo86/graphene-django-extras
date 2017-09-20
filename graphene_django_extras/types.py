# -*- coding: utf-8 -*-
from collections import OrderedDict

from django.utils.functional import SimpleLazyObject
from graphene import Field, InputField, ObjectType, Int
from graphene.types.base import BaseOptions
from graphene.types.inputobjecttype import InputObjectType, InputObjectTypeContainer
from graphene.types.utils import yank_fields_from_attrs
from graphene_django.utils import is_valid_django_model, DJANGO_FILTER_INSTALLED

from .base_types import generic_django_object_type_factory
from .converter import construct_fields
from .fields import DjangoListField
from .registry import get_global_registry, Registry

__all__ = ('DjangoObjectType', 'DjangoInputObjectType', 'DjangoPaginatedObjectListType')


class DjangoObjectOptions(BaseOptions):
    fields = None
    input_fields = None
    interfaces = ()
    model = None
    registry = None
    connection = None
    create_container = None
    results_field_name = None
    filter_fields = ()
    input_for = None


class DjangoObjectType(ObjectType):
    @classmethod
    def __init_subclass_with_meta__(cls, model=None, registry=None, skip_registry=False,
                                    only_fields=(), exclude_fields=(), filter_fields=None,
                                    interfaces=(), **options):
        assert is_valid_django_model(model), (
            'You need to pass a valid Django Model in {}.Meta, received "{}".'
        ).format(cls.__name__, model)

        if not registry:
            registry = get_global_registry()

        assert isinstance(registry, Registry), (
            'The attribute registry in {} needs to be an instance of '
            'Registry, received "{}".'
        ).format(cls.__name__, registry)

        if not DJANGO_FILTER_INSTALLED and filter_fields:
            raise Exception("Can only set filter_fields if Django-Filter is installed")

        django_fields = yank_fields_from_attrs(
            construct_fields(model, registry, only_fields, exclude_fields),
            _as=Field,
        )

        _meta = DjangoObjectOptions(cls)
        _meta.model = model
        _meta.registry = registry
        _meta.filter_fields = filter_fields
        _meta.fields = django_fields

        super(DjangoObjectType, cls).__init_subclass_with_meta__(_meta=_meta, interfaces=interfaces, **options)

        if not skip_registry:
            registry.register(cls)

    def resolve_id(self, info):
        return self.pk

    @classmethod
    def is_type_of(cls, root, info):
        if isinstance(root, SimpleLazyObject):
            root._setup()
            root = root._wrapped
        if isinstance(root, cls):
            return True
        if not is_valid_django_model(type(root)):
            raise Exception((
                'Received incompatible instance "{}".'
            ).format(root))
        model = root._meta.model
        return model == cls._meta.model

    @classmethod
    def get_node(cls, info, id):
        try:
            return cls._meta.model.objects.get(pk=id)
        except cls._meta.model.DoesNotExist:
            return None


class DjangoInputObjectType(InputObjectType):
    @classmethod
    def __init_subclass_with_meta__(cls, model=None, container=None, registry=None, skip_registry=False,
                                    connection=None, use_connection=None, for_update=False,
                                    only_fields=(), exclude_fields=(), filter_fields=None,
                                    input_for="create", interfaces=(), **options):
        assert is_valid_django_model(model), (
            'You need to pass a valid Django Model in {}.Meta, received "{}".'
        ).format(cls.__name__, model)

        if not registry:
            registry = get_global_registry()

        assert isinstance(registry, Registry), (
            'The attribute registry in {} needs to be an instance of '
            'Registry, received "{}".'
        ).format(cls.__name__, registry)

        assert input_for.lower not in ('create', 'delete', 'update'), (
            'You need to pass a valid input_for value in {}.Meta, received "{}".'
        ).format(cls.__name__, input_for)

        input_for = input_for.lower()

        if not DJANGO_FILTER_INSTALLED and filter_fields:
            raise Exception("Can only set filter_fields if Django-Filter is installed")

        django_fields = yank_fields_from_attrs(
            construct_fields(model, registry, only_fields, exclude_fields, input_for),
            _as=Field,
        )

        django_input_fields = yank_fields_from_attrs(
            construct_fields(model, registry, only_fields, exclude_fields, input_for),
            _as=InputField,
        )

        if container is None:
            container = type(cls.__name__, (InputObjectTypeContainer, cls), {})

        _meta = DjangoObjectOptions(cls)
        _meta.by_polar = True
        _meta.model = model
        _meta.registry = registry
        _meta.filter_fields = filter_fields
        # _meta.fields = django_fields
        _meta.fields = django_input_fields
        _meta.input_fields = django_input_fields
        _meta.container = container
        _meta.connection = connection
        _meta.input_for = input_for

        super(InputObjectType, cls).__init_subclass_with_meta__(_meta=_meta, interfaces=interfaces, **options)

        if not skip_registry:
            registry.register(cls, for_input=True)

    @classmethod
    def get_type(cls):
        """
        This function is called when the unmounted type (InputObjectType instance)
        is mounted (as a Field, InputField or Argument)
        """
        return cls


class DjangoPaginatedObjectListType(ObjectType):

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, model=None, results_field_name=None, pagination=None,
                                    only_fields=(), exclude_fields=(), filter_fields=None,
                                    interfaces=(), **options):

        assert is_valid_django_model(model), (
            'You need to pass a valid Django Model in {}.Meta, received "{}".'
        ).format(cls.__name__, model)

        if not DJANGO_FILTER_INSTALLED and filter_fields:
            raise Exception("Can only set filter_fields if Django-Filter is installed")

        if not results_field_name:
            results_field_name = 'results'

        baseType = get_global_registry().get_type_for_model(model)

        if not baseType:
            baseType = generic_django_object_type_factory(DjangoObjectType, model, only_fields,
                                                          exclude_fields, filter_fields)
        else:
            filter_fields = filter_fields or baseType._meta.filter_fields

        if pagination:
            result_container = pagination.get_pagination_field(baseType)
        else:
            result_container = DjangoListField(baseType)

        _meta = DjangoObjectOptions(cls)
        _meta.model = model
        _meta.baseType = baseType
        _meta.results_field_name = results_field_name
        _meta.filter_fields = filter_fields
        _meta.exclude_fields = exclude_fields
        _meta.only_fields = only_fields
        _meta.fields = OrderedDict([
            (results_field_name, result_container),
            ('count', Field(Int, name='totalCount', required=True, description="Total count of matches elements"))
        ])

        super(DjangoPaginatedObjectListType, cls).__init_subclass_with_meta__(_meta=_meta, interfaces=interfaces, **options)

    @classmethod
    def getOne(cls):
        return cls._meta.baseType
