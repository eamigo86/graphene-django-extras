# -*- coding: utf-8 -*-
from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _
from graphene import Boolean, List, Field, ID, Argument, ObjectType, InputField, InputObjectType
from graphene.types.base import BaseOptions
from graphene.types.utils import yank_fields_from_attrs
from graphene.utils.deprecated import warn_deprecation
from graphene.utils.get_unbound_function import get_unbound_function
from graphene.utils.props import props
from graphene_django.rest_framework.types import ErrorType

from .base_types import generic_django_object_type_factory
from .converter import construct_fields
from .registry import get_global_registry
from .types import DjangoObjectType
from .utils import kwargs_formatter, get_Object_or_None


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

    ok = Boolean(description=_('Boolean field that return mutation result request.'))
    errors = List(ErrorType, description=_('May contain more than one error for same field.'))

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, serializer_class=None, only_fields=(), exclude_fields=(),
                                    create_resolver=None, delete_resolver=None, update_resolver=None,
                                    input_field_name=None, output_field_name=None, preprocess_kwargs=None,
                                    **options):

        if not serializer_class:
            raise Exception('serializer_class is required on all DjangoSerializerMutation')

        model = serializer_class.Meta.model

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

        bases = (InputObjectType,)
        # if input_class:
            # bases += (input_class,)

        registry = get_global_registry()

        """
        django_fields = yank_fields_from_attrs(
            construct_fields(model, registry, only_fields, exclude_fields),
            _as=Field
        )
        """
        outputType = registry.get_type_for_model(model)

        if not outputType:
            outputType = generic_django_object_type_factory(DjangoObjectType, model)

        django_fields = OrderedDict({output_field_name: Field(outputType)})

        django_input_fields = {}
        global_arguments = {}
        for operation in ('create', 'delete', 'update'):
            global_arguments.update({operation: OrderedDict()})

            input_fields = yank_fields_from_attrs(
                construct_fields(model, registry, only_fields, exclude_fields, operation),
                _as=InputField
            )

            django_input_fields.update({
                operation: input_fields
            })

            if operation != 'delete':
                global_arguments[operation].update({
                    input_field_name: Argument(type(
                        '{}{}Input'.format(model.__name__, operation.capitalize()),
                        bases,
                        input_fields
                    ), required=True)
                })
            else:
                global_arguments[operation].update({
                    'id': Argument(ID, required=True, description=_('Django object unique identification field'))
                })
            global_arguments[operation].update(arguments)

        if not create_resolver:
            create_mutation = getattr(cls, 'create_mutation', None)
            create_resolver = get_unbound_function(create_mutation) if create_mutation else None

        if not delete_resolver:
            delete_mutation = getattr(cls, 'delete_mutation', None)
            delete_resolver = get_unbound_function(delete_mutation) if delete_mutation else None

        if not update_resolver:
            update_mutation = getattr(cls, 'update_mutation', None)
            update_resolver = get_unbound_function(update_mutation) if update_mutation else None

        assert (create_resolver or delete_resolver or update_resolver), \
            _('All the SerializerMutations must define at least one of his mutations methods in it: '
              '\'create_mutation\', \'delete_mutation\' or \'update_mutation\'')

        preprocess_kwargs = preprocess_kwargs or kwargs_formatter

        _meta = SerializerMutationOptions(cls)
        _meta.output = cls
        _meta.arguments = global_arguments
        _meta.fields = django_fields
        _meta.create_resolver = create_resolver
        _meta.delete_resolver = delete_resolver
        _meta.update_resolver = update_resolver
        _meta.model = model
        _meta.serializer_class = serializer_class
        _meta.input_field_name = input_field_name
        _meta.output_field_name = output_field_name
        _meta.preprocess_kwargs = preprocess_kwargs

        super(DjangoSerializerMutation, cls).__init_subclass_with_meta__(_meta=_meta, **options)

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
    def create_mutation(cls, root, info, **kwargs):
        new_obj = kwargs.get(cls._meta.input_field_name, None)

        if new_obj:
            serializer = cls._meta.serializer_class(data=new_obj)

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
    def delete_mutation(cls, root, info, **kwargs):
        pk = kwargs.get('id', None)

        if id:
            model = cls._meta.model
            old_obj = get_Object_or_None(model, pk=pk)
            if old_obj:
                old_obj.delete()
                return cls.perform_mutate(None, info)
            else:
                errors = [
                    ErrorType(
                        field='id',
                        messages=['A {} obj with id {} do not exist'.format(model.__name__, pk)])
                ]
            return cls.get_errors(errors)

    @classmethod
    def update_mutation(cls, root, info, **kwargs):
        new_obj = kwargs.get(cls._meta.input_field_name, None)

        if new_obj:
            model = cls._meta.model
            id = new_obj.pop('id')
            old_obj = get_Object_or_None(model, pk=id)
            if old_obj:
                new_obj_serialized = dict(cls._meta.serializer_class(old_obj).data)
                new_obj_serialized.update(new_obj)
                serializer = cls._meta.serializer_class(old_obj, data=new_obj_serialized)

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
    def CreateField(cls, *args, **kwargs):
        kwargs = cls._meta.preprocess_kwargs(**kwargs)

        return Field(
            cls._meta.output, args=cls._meta.arguments['create'], resolver=cls._meta.create_resolver, **kwargs
        )

    @classmethod
    def DeleteField(cls, *args, **kwargs):
        kwargs = cls._meta.preprocess_kwargs(**kwargs)

        return Field(
            cls._meta.output, args=cls._meta.arguments['delete'], resolver=cls._meta.delete_resolver, **kwargs
        )

    @classmethod
    def UpdateField(cls, *args, **kwargs):
        kwargs = cls._meta.preprocess_kwargs(**kwargs)

        return Field(
            cls._meta.output, args=cls._meta.arguments['update'], resolver=cls._meta.update_resolver, **kwargs
        )
