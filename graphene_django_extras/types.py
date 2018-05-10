# -*- coding: utf-8 -*-
from collections import OrderedDict

from django.db.models import QuerySet
from django.utils.functional import SimpleLazyObject
from graphene import Field, InputField, ObjectType, Int, Argument, ID, Boolean, List
from graphene.types.base import BaseOptions
from graphene.types.inputobjecttype import InputObjectType, InputObjectTypeContainer
from graphene.types.utils import yank_fields_from_attrs
from graphene.utils.deprecated import warn_deprecation
from graphene.utils.props import props
from graphene_django.fields import DjangoListField
from graphene_django.rest_framework.types import ErrorType
from graphene_django.utils import is_valid_django_model, DJANGO_FILTER_INSTALLED, maybe_queryset

from .base_types import DjangoListObjectBase, factory_type
from .converter import construct_fields
from .fields import DjangoObjectField, DjangoListObjectField
from .paginations.pagination import BaseDjangoGraphqlPagination
from .registry import get_global_registry, Registry
from .settings import graphql_api_settings
from .utils import get_Object_or_None, queryset_factory

__all__ = ('DjangoObjectType', 'DjangoInputObjectType', 'DjangoListObjectType', 'DjangoSerializerType')


class DjangoObjectOptions(BaseOptions):
    fields = None
    input_fields = None
    interfaces = ()
    model = None
    queryset = None
    registry = None
    connection = None
    create_container = None
    results_field_name = None
    filter_fields = ()
    input_for = None
    filterset_class = None


class DjangoSerializerOptions(BaseOptions):
    model = None
    queryset = None
    serializer_class = None

    arguments = None
    fields = None
    input_fields = None
    input_field_name = None

    mutation_output = None
    output_field_name = None
    output_type = None
    output_list_type = None


class DjangoObjectType(ObjectType):
    @classmethod
    def __init_subclass_with_meta__(
        cls,
        model=None,
        registry=None,
        skip_registry=False,
        only_fields=(),
        exclude_fields=(),
        filter_fields=None,
        interfaces=(),
        filterset_class=None,
        **options
    ):
        assert is_valid_django_model(model), (
            'You need to pass a valid Django Model in {}.Meta, received "{}".'
        ).format(cls.__name__, model)

        if not registry:
            registry = get_global_registry()

        assert isinstance(registry, Registry), (
            'The attribute registry in {} needs to be an instance of '
            'Registry, received "{}".'
        ).format(cls.__name__, registry)

        if not DJANGO_FILTER_INSTALLED and (filter_fields or filterset_class):
            raise Exception(
                "Can only set filter_fields or filterset_class if Django-Filter is installed"
            )

        django_fields = yank_fields_from_attrs(
            construct_fields(model, registry, only_fields, exclude_fields),
            _as=Field,
        )

        _meta = DjangoObjectOptions(cls)
        _meta.model = model
        _meta.registry = registry
        _meta.filter_fields = filter_fields
        _meta.fields = django_fields
        _meta.filterset_class = filterset_class

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
                                    connection=None, use_connection=None, only_fields=(), exclude_fields=(),
                                    filter_fields=None, input_for="create", nested_fields=False, **options):
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
            construct_fields(model, registry, only_fields, exclude_fields, None, nested_fields),
            _as=Field, sort=False
        )

        django_input_fields = yank_fields_from_attrs(
            construct_fields(model, registry, only_fields, exclude_fields, input_for, nested_fields),
            _as=InputField, sort=False
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

        super(InputObjectType, cls).__init_subclass_with_meta__(_meta=_meta, **options)

        if not skip_registry:
            registry.register(cls, for_input=input_for)

    @classmethod
    def get_type(cls):
        """
        This function is called when the unmounted type (InputObjectType instance)
        is mounted (as a Field, InputField or Argument)
        """
        return cls


class DjangoListObjectType(ObjectType):

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        model=None,
        results_field_name=None,
        pagination=None,
        only_fields=(),
        exclude_fields=(),
        filter_fields=None,
        queryset=None,
        filterset_class=None,
        **options
    ):

        assert is_valid_django_model(model), (
            'You need to pass a valid Django Model in {}.Meta, received "{}".'
        ).format(cls.__name__, model)

        if not DJANGO_FILTER_INSTALLED and filter_fields:
            raise Exception("Can only set filter_fields if Django-Filter is installed")

        assert isinstance(queryset, QuerySet) or queryset is None, (
            'The attribute queryset in {} needs to be an instance of '
            'Django model queryset, received "{}".'
        ).format(cls.__name__, queryset)

        results_field_name = results_field_name or 'results'

        baseType = get_global_registry().get_type_for_model(model)

        if not baseType:
            factory_kwargs = {
                'model': model,
                'only_fields': only_fields,
                'exclude_fields': exclude_fields,
                'filter_fields': filter_fields,
                'filterset_class': filterset_class,
                'pagination': pagination,
                'queryset': queryset,
                'skip_registry': False
            }
            baseType = factory_type('output', DjangoObjectType, **factory_kwargs)

        filter_fields = filter_fields or baseType._meta.filter_fields

        if pagination:
            result_container = pagination.get_pagination_field(baseType)
        else:
            global_paginator = graphql_api_settings.DEFAULT_PAGINATION_CLASS
            if global_paginator:
                assert issubclass(
                    global_paginator, BaseDjangoGraphqlPagination
                ), (
                    'You need to pass a valid DjangoGraphqlPagination class in {}.Meta, received "{}".'
                ).format(cls.__name__, global_paginator)

                global_paginator = global_paginator()
                result_container = global_paginator.get_pagination_field(
                    baseType
                )
            else:
                result_container = DjangoListField(baseType)

        _meta = DjangoObjectOptions(cls)
        _meta.model = model
        _meta.queryset = queryset
        _meta.baseType = baseType
        _meta.results_field_name = results_field_name
        _meta.filter_fields = filter_fields
        _meta.exclude_fields = exclude_fields
        _meta.only_fields = only_fields
        _meta.filterset_class = filterset_class
        _meta.fields = OrderedDict(
            [
                (results_field_name, result_container), (
                    'count',
                    Field(
                        Int,
                        name='totalCount',
                        description="Total count of matches elements"
                    )
                )
            ]
        )

        super(DjangoListObjectType, cls).__init_subclass_with_meta__(_meta=_meta, **options)

    @classmethod
    def RetrieveField(cls, *args, **kwargs):
        return DjangoObjectField(cls._meta.baseType, **kwargs)

    @classmethod
    def BaseType(cls):
        return cls._meta.baseType


class DjangoSerializerType(ObjectType):
    """
        DjangoSerializerType definition
    """

    ok = Boolean(
        description='Boolean field that return mutation result request.'
    )
    errors = List(ErrorType, description='Errors list for the field')

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, serializer_class=None, queryset=None, only_fields=(), exclude_fields=(),
                                    pagination=None, input_field_name=None, output_field_name=None,
                                    results_field_name=None, nested_fields=False, filter_fields=None, description='',
                                    filterset_class=None, **options):

        if not serializer_class:
            raise Exception('serializer_class is required on all ModelSerializerType')

        model = serializer_class.Meta.model

        description = description or 'ModelSerializerType for {} model'.format(model.__name__)

        input_field_name = input_field_name or 'new_{}'.format(model._meta.model_name)
        output_field_name = output_field_name or model._meta.model_name

        input_class = getattr(cls, 'Arguments', None)
        if not input_class:
            input_class = getattr(cls, 'Input', None)
            if input_class:
                warn_deprecation(("Please use {name}.Arguments instead of {name}.Input."
                                  "Input is now only used in ClientMutationID.\nRead more: "
                                  "https://github.com/graphql-python/graphene/blob/2.0/UPGRADE-v2.0.md#mutation-input").
                                 format(name=cls.__name__))
        if input_class:
            arguments = props(input_class)
        else:
            arguments = {}

        registry = get_global_registry()

        factory_kwargs = {
            'model': model,
            'only_fields': only_fields,
            'exclude_fields': exclude_fields,
            'filter_fields': filter_fields,
            'pagination': pagination,
            'queryset': queryset,
            'nested_fields': nested_fields,
            'registry': registry,
            'skip_registry': False,
            'filterset_class': filterset_class
        }

        output_type = registry.get_type_for_model(model)

        if not output_type:
            output_type = factory_type('output', DjangoObjectType, **factory_kwargs)

        output_list_type = factory_type('list', DjangoListObjectType, **factory_kwargs)

        django_fields = OrderedDict({output_field_name: Field(output_type)})

        global_arguments = {}
        for operation in ('create', 'delete', 'update'):
            global_arguments.update({operation: OrderedDict()})

            if operation != 'delete':
                input_type = registry.get_type_for_model(model, for_input=operation)

                if not input_type:
                    factory_kwargs.update({'skip_registry': True})
                    input_type = factory_type('input', DjangoInputObjectType, operation, **factory_kwargs)

                global_arguments[operation].update({
                    input_field_name: Argument(input_type, required=True)
                })
            else:
                global_arguments[operation].update({
                    'id': Argument(ID, required=True, description='Django object unique identification field')
                })
            global_arguments[operation].update(arguments)

        _meta = DjangoSerializerOptions(cls)
        _meta.mutation_output = cls
        _meta.arguments = global_arguments
        _meta.fields = django_fields
        _meta.output_type = output_type
        _meta.output_list_type = output_list_type
        _meta.model = model
        _meta.queryset = queryset or model._default_manager
        _meta.serializer_class = serializer_class
        _meta.input_field_name = input_field_name
        _meta.output_field_name = output_field_name

        super(DjangoSerializerType, cls).__init_subclass_with_meta__(_meta=_meta, description=description, **options)

    @classmethod
    def list_object_type(cls):
        return cls._meta.output_list_type

    @classmethod
    def object_type(cls):
        return cls._meta.output_type

    @classmethod
    def get_errors(cls, errors):
        errors_dict = {
            cls._meta.output_field_name: None,
            'ok': False,
            'errors': errors
        }

        return cls(**errors_dict)

    @classmethod
    def perform_mutate(cls, obj, info):
        resp = {
            cls._meta.output_field_name: obj,
            'ok': True,
            'errors': None
        }

        return cls(**resp)

    @classmethod
    def get_serializer_kwargs(cls, root, info, **kwargs):
        return {}

    @classmethod
    def create(cls, root, info, **kwargs):
        new_obj = kwargs.get(cls._meta.input_field_name, None)

        if new_obj:
            serializer = cls._meta.serializer_class(
                data=new_obj,
                **cls.get_serializer_kwargs(root, info, **kwargs)
            )

            if serializer.is_valid():
                obj = serializer.save()
                return cls.perform_mutate(obj, info)

            else:
                errors = [
                    ErrorType(field=key, messages=value)
                    for key, value in serializer.errors.items()
                ]
                return cls.get_errors(errors)

    @classmethod
    def delete(cls, root, info, **kwargs):
        pk = kwargs.get('id', None)

        if id:
            model = cls._meta.model
            old_obj = get_Object_or_None(model, pk=pk)
            if old_obj:
                old_obj.delete()
                old_obj.id = pk

                return cls.perform_mutate(old_obj, info)
            else:
                errors = [
                    ErrorType(
                        field='id',
                        messages=['A {} obj with id {} do not exist'.format(model.__name__, pk)])
                ]
            return cls.get_errors(errors)

    @classmethod
    def update(cls, root, info, **kwargs):
        new_obj = kwargs.get(cls._meta.input_field_name, None)

        if new_obj:
            model = cls._meta.model
            id = new_obj.pop('id')
            old_obj = get_Object_or_None(model, pk=id)
            if old_obj:
                new_obj_serialized = dict(cls._meta.serializer_class(
                    old_obj,
                    **cls.get_serializer_kwargs(root, info, **kwargs)
                ).data)
                new_obj_serialized.update(new_obj)
                serializer = cls._meta.serializer_class(
                    old_obj,
                    data=new_obj_serialized,
                    **cls.get_serializer_kwargs(root, info, **kwargs)
                )

                if serializer.is_valid():
                    obj = serializer.save()
                    return cls.perform_mutate(obj, info)
                else:
                    errors = [
                        ErrorType(field=key, messages=value)
                        for key, value in serializer.errors.items()
                    ]
            else:
                errors = [
                    ErrorType(
                        field='id',
                        messages=['A {} obj with id: {} do not exist'.format(model.__name__, id)])
                ]
            return cls.get_errors(errors)

    @classmethod
    def retrieve(cls, manager, root, info, **kwargs):
        id = kwargs.pop('id', None)

        try:
            return manager.get_queryset().get(pk=id)
        except manager.model.DoesNotExist:
            return None

    @classmethod
    def list(cls, manager, filterset_class, filtering_args, root, info, **kwargs):

        qs = queryset_factory(cls._meta.queryset or manager, info.field_asts, info.fragments, **kwargs)

        filter_kwargs = {k: v for k, v in kwargs.items() if k in filtering_args}

        qs = filterset_class(data=filter_kwargs, queryset=qs).qs
        count = qs.count()

        return DjangoListObjectBase(
            count=count,
            results=maybe_queryset(qs),
            results_field_name=cls.list_object_type()._meta.results_field_name
        )

    @classmethod
    def RetrieveField(cls, *args, **kwargs):
        return DjangoObjectField(cls._meta.output_type, resolver=cls.retrieve, **kwargs)

    @classmethod
    def ListField(cls, *args, **kwargs):
        return DjangoListObjectField(cls._meta.output_list_type, resolver=cls.list, **kwargs)

    @classmethod
    def CreateField(cls, *args, **kwargs):
        return Field(
            cls._meta.mutation_output, args=cls._meta.arguments['create'], resolver=cls.create, **kwargs
        )

    @classmethod
    def DeleteField(cls, *args, **kwargs):
        return Field(
            cls._meta.mutation_output, args=cls._meta.arguments['delete'], resolver=cls.delete, **kwargs
        )

    @classmethod
    def UpdateField(cls, *args, **kwargs):
        return Field(
            cls._meta.mutation_output, args=cls._meta.arguments['update'], resolver=cls.update, **kwargs
        )

    @classmethod
    def QueryFields(cls, *args, **kwargs):
        retrieve_field = cls.RetrieveField(*args, **kwargs)
        list_field = cls.ListField(*args, **kwargs)

        return retrieve_field, list_field

    @classmethod
    def MutationFields(cls, *args, **kwargs):
        create_field = cls.CreateField(*args, **kwargs)
        delete_field = cls.DeleteField(*args, **kwargs)
        update_field = cls.UpdateField(*args, **kwargs)

        return create_field, delete_field, update_field
