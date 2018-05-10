# -*- coding: utf-8 -*-
from collections import OrderedDict

from django.core.exceptions import ValidationError
from graphene import Boolean, List, Field, ID, Argument, ObjectType
from graphene.types.base import BaseOptions
from graphene.utils.deprecated import warn_deprecation
from graphene.utils.get_unbound_function import get_unbound_function
from graphene.utils.props import props
from graphene_django.rest_framework.types import ErrorType

from .base_types import factory_type
from .registry import get_global_registry
from .types import DjangoObjectType, DjangoInputObjectType
from .utils import get_Object_or_None, parse_validation_exc


class SerializerMutationOptions(BaseOptions):
    fields = None
    input_fields = None
    interfaces = ()
    serializer_class = None
    action = None
    arguments = None
    output = None
    resolver = None


class DjangoSerializerMutation(ObjectType):
    """
        Serializer Mutation Type Definition
    """

    ok = Boolean(description='Boolean field that return mutation result request.')
    errors = List(ErrorType, description='Errors list for the field')

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, serializer_class=None, only_fields=(), exclude_fields=(),
                                    save_resolver=None, delete_resolver=None,
                                    input_field_name=None, output_field_name=None, description='',
                                    nested_fields=False, **options):

        if not serializer_class:
            raise Exception('serializer_class is required on all DjangoSerializerMutation')

        model = serializer_class.Meta.model

        description = description or 'SerializerMutation for {} model'.format(model.__name__)

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
            'nested_fields': nested_fields,
            'registry': registry,
            'skip_registry': False
        }

        output_type = registry.get_type_for_model(model)

        if not output_type:
            output_type = factory_type('output', DjangoObjectType, **factory_kwargs)

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

        if not save_resolver:
            save_mutation = getattr(cls, 'save_mutation', None)
            save_resolver = get_unbound_function(save_mutation) if save_mutation else None

        if not delete_resolver:
            delete_mutation = getattr(cls, 'delete_mutation', None)
            delete_resolver = get_unbound_function(delete_mutation) if delete_mutation else None

        assert (save_resolver or delete_resolver), \
            'All the SerializerMutations must define at least one of this class  methods: ' \
            '\'save_mutation\' or \'delete_mutation\''

        _meta = SerializerMutationOptions(cls)
        _meta.output = cls
        _meta.arguments = global_arguments
        _meta.fields = django_fields
        _meta.output_type = output_type
        _meta.save_resolver = save_resolver
        _meta.delete_resolver = delete_resolver
        _meta.model = model
        _meta.serializer_class = serializer_class
        _meta.input_field_name = input_field_name
        _meta.output_field_name = output_field_name

        super(DjangoSerializerMutation, cls).__init_subclass_with_meta__(_meta=_meta, description=description,
                                                                         **options)

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
    def save_mutation(cls, root, info, **kwargs):
        new_obj = kwargs.get(cls._meta.input_field_name, None)
        files = info.context.FILES
        data = dict(new_obj, **files)

        if new_obj:
            model = cls._meta.model
            id = new_obj.pop('id', None)
            if id:
                old_obj = get_Object_or_None(model, pk=id)
                if old_obj:
                    serializer = cls._meta.serializer_class(
                        old_obj,
                        data=data,
                        partial=True,
                        **cls.get_serializer_kwargs(root, info, **kwargs)
                    )
                else:
                    return cls.get_errors([
                        ErrorType(
                            field='id',
                            messages=['A {} obj with id: {} do not exist'.format(model.__name__, id)])
                    ])
            else:
                serializer = cls._meta.serializer_class(
                    data=data,
                    **cls.get_serializer_kwargs(root, info, **kwargs)
                )

            if serializer.is_valid():
                try:
                    obj = serializer.save()
                    return cls.perform_mutate(obj, info)

                except ValidationError as e:
                    return cls.get_errors([
                        ErrorType(**errors)
                        for errors in parse_validation_exc(e)
                    ])
            else:
                return cls.get_errors([
                    ErrorType(field=key, messages=value)
                    for key, value in serializer.errors.items()
                ])

    @classmethod
    def delete_mutation(cls, root, info, **kwargs):
        pk = kwargs.get('id', None)

        if id:
            model = cls._meta.model
            old_obj = get_Object_or_None(model, pk=pk)
            if old_obj:
                old_obj.delete()
                old_obj.id = pk

                return cls.perform_mutate(old_obj, info)
            else:
                return cls.get_errors([
                    ErrorType(
                        field='id',
                        messages=['A {} obj with id {} do not exist'.format(model.__name__, pk)])
                ])

    @classmethod
    def CreateField(cls, *args, **kwargs):
        return Field(
            cls._meta.output, args=cls._meta.arguments['create'], resolver=cls._meta.save_resolver, **kwargs
        )

    @classmethod
    def DeleteField(cls, *args, **kwargs):
        return Field(
            cls._meta.output, args=cls._meta.arguments['delete'], resolver=cls._meta.delete_resolver, **kwargs
        )

    @classmethod
    def UpdateField(cls, *args, **kwargs):
        return Field(
            cls._meta.output, args=cls._meta.arguments['update'], resolver=cls._meta.save_resolver, **kwargs
        )

    @classmethod
    def MutationFields(cls, *args, **kwargs):
        create_field = cls.CreateField(*args, **kwargs)
        delete_field = cls.DeleteField(*args, **kwargs)
        update_field = cls.UpdateField(*args, **kwargs)

        return create_field, delete_field, update_field
