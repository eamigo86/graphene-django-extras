# -*- coding: utf-8 -*-
from collections import OrderedDict

from graphene import Boolean, List, Field, ID, Argument, ObjectType
from graphene.types.base import BaseOptions
from graphene.utils.deprecated import warn_deprecation
from graphene.utils.props import props
from graphene_django.types import ErrorType
from graphene_django.constants import MUTATION_ERRORS_FLAG

from .base_types import factory_type
from .registry import get_global_registry
from .types import DjangoObjectType, DjangoInputObjectType
from .utils import get_Object_or_None


class SerializerMutationOptions(BaseOptions):
    fields = None
    input_fields = None
    interfaces = ()
    serializer_class = None
    action = None
    arguments = None
    output = None
    resolver = None
    nested_fields = None


class DjangoSerializerMutation(ObjectType):
    """
        Serializer Mutation Type Definition
    """

    ok = Boolean(
        description="Boolean field that return mutation result request.")
    errors = List(ErrorType, description="Errors list for the field")

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        serializer_class=None,
        only_fields=(),
        include_fields=(),
        exclude_fields=(),
        input_field_name=None,
        output_field_name=None,
        description="",
        nested_fields=(),
        **options,
    ):
        non_required_fields = options["non_required_fields"]
        input_type_name = options["input_type"]
        extra_fields = options["extra_fields"]
        del options["non_required_fields"]
        del options["input_type"]
        del options["extra_fields"]
        if not serializer_class:
            raise Exception(
                "serializer_class is required on all DjangoSerializerMutation"
            )

        model = serializer_class.Meta.model

        description = description or f"SerializerMutation for {model.__name__} model"
        input_field_name = input_field_name or "new_{}".format(
            model.API_SCHEMA.graphql_schema[0].class_name_prefix or model._meta.model_name)
        input_field_name_dict = {
            'create': input_field_name
        }
        output_field_name = output_field_name or model._meta.model_name

        input_class = getattr(cls, "Arguments", None)
        if not input_class:
            input_class = getattr(cls, "Input", None)
            if input_class:
                warn_deprecation(
                    (
                        "Please use {name}.Arguments instead of {name}.Input."
                        "Input is now only used in ClientMutationID.\nRead more: "
                        "https://github.com/graphql-python/graphene/blob/2.0/UPGRADE-v2.0.md#mutation-input"
                    ).format(name=cls.__name__)
                )
        arguments = props(input_class) if input_class else {}
        registry = get_global_registry()

        factory_kwargs = {
            "model": model,
            "only_fields": only_fields,
            "include_fields": include_fields,
            "exclude_fields": exclude_fields,
            "nested_fields": nested_fields,
            "registry": registry,
            "skip_registry": False,
            "non_required_fields": non_required_fields,
            "extra_fields": extra_fields,
        }

        if input_type_name:
            factory_kwargs["name"] = input_type_name

        output_type = registry.get_type_for_model(model)

        if not output_type:
            output_type = factory_type(
                "output", DjangoObjectType, **factory_kwargs)

        django_fields = OrderedDict({output_field_name: Field(output_type)})

        global_arguments = {}

        for operation in ("create", "delete", "update"):
            global_arguments[operation] = OrderedDict()

            if operation != "delete":
                if operation == 'update':
                    input_field_name = f"update_{model.API_SCHEMA.graphql_schema[0].class_name_prefix or model._meta.model_name}"
                    input_field_name_dict['update'] = input_field_name
                input_type = (
                    factory_type(
                        "input", DjangoInputObjectType, operation, **factory_kwargs
                    )
                    if input_type_name
                    else registry.get_type_for_model(model, for_input=operation)
                    or factory_type(
                        "input", DjangoInputObjectType, operation, **factory_kwargs
                    )
                )

                global_arguments[operation].update(
                    {input_field_name: Argument(input_type, required=True)}
                )
            else:
                global_arguments[operation].update(
                    {
                        "id": Argument(
                            ID,
                            required=True,
                            description="Django object unique identification field",
                        )
                    }
                )
            global_arguments[operation].update(arguments)

        _meta = SerializerMutationOptions(cls)
        _meta.output = cls
        _meta.arguments = global_arguments
        _meta.fields = django_fields
        _meta.output_type = output_type
        _meta.model = model
        _meta.serializer_class = serializer_class
        _meta.input_field_name = input_field_name_dict
        _meta.output_field_name = output_field_name
        _meta.nested_fields = nested_fields
        _meta.non_required_fields = non_required_fields
        _meta.extra_fields = extra_fields
        super(DjangoSerializerMutation, cls).__init_subclass_with_meta__(
            _meta=_meta, description=description, **options
        )

    @classmethod
    def get_errors(cls, errors):
        errors_dict = {cls._meta.output_field_name: None,
                       "ok": False, "errors": errors}

        return cls(**errors_dict)

    @classmethod
    def perform_mutate(cls, obj, info):
        resp = {cls._meta.output_field_name: obj, "ok": True, "errors": None}

        return cls(**resp)

    @classmethod
    def get_serializer_kwargs(cls, root, info, **kwargs):
        return {}

    @classmethod
    def manage_nested_fields(cls, data, root, info):
        nested_objs = {}
        if cls._meta.nested_fields and type(cls._meta.nested_fields) == dict:
            for field in cls._meta.nested_fields:
                if sub_data := data.pop(field, None):
                    serialized_data = cls._meta.nested_fields[field](
                        data=sub_data, many=type(sub_data) == list
                    )

                    ok, result = cls.save(serialized_data, root, info)
                    if not ok:
                        return cls.get_errors(result)
                    if type(sub_data) == list:
                        nested_objs[field] = result
                    else:
                        data.update({field: result.id})
        return nested_objs

    @classmethod
    def create(cls, root, info, **kwargs):
        data = kwargs.get(cls._meta.input_field_name['create'])
        m2m_dict = {}
        if non_required_fields := cls._meta.non_required_fields:
            non_required_fields_list = [field.name for field in non_required_fields]
            m2m_fields = [
                field.attname for field in cls._meta.model._meta.local_many_to_many if field.attname in non_required_fields_list]
            for m2m_field in m2m_fields:
                if data.get(m2m_field):
                    m2m_dict[m2m_field] = data.pop(m2m_field)
                else:
                    data[m2m_field] = []
        request_type = info.context.META.get("CONTENT_TYPE", "")
        if "multipart/form-data" in request_type:
            data.update(dict(info.context.FILES.items()))

        nested_objs = cls.manage_nested_fields(data, root, info)
        serializer = cls._meta.serializer_class(
            data=data, context=info.context.user, **cls.get_serializer_kwargs(root, info, **kwargs)
        )

        ok, obj = cls.save(serializer, root, info)
        for m2m_field, value in m2m_dict.items():
            field = getattr(obj, m2m_field)
            field.set(value)
        if not ok:
            return cls.get_errors(obj)
        elif nested_objs:
            [getattr(obj, field).add(*objs)
             for field, objs in nested_objs.items()]
        return cls.perform_mutate(obj, info)

    @classmethod
    def delete(cls, root, info, **kwargs):
        pk = kwargs.get("id")

        if old_obj := get_Object_or_None(
            cls._meta.model, info, type='delete', pk=pk
        ):
            old_obj.delete()
            old_obj.id = pk
            return cls.perform_mutate(old_obj, info)
        else:
            # Atomic transaction support
            cls._set_errors_flag_to_context(info)
            return cls.get_errors(
                [
                    ErrorType(
                        field="id",
                        messages=[
                            f"A {cls._meta.model.__name__} obj with id {pk} do not exist"
                        ],
                    )
                ]
            )

    @classmethod
    def update(cls, root, info, **kwargs):
        data = kwargs.get(cls._meta.input_field_name['update'])
        m2m_dict = {}
        if non_required_fields := cls._meta.non_required_fields:
            non_required_fields_list = [field.name for field in non_required_fields ]
            m2m_fields = [
                field.attname for field in cls._meta.model._meta.local_many_to_many if field.attname in non_required_fields_list]
            for m2m_field in m2m_fields:
                if data.get(m2m_field):
                    m2m_dict[m2m_field] = data.pop(m2m_field)
        request_type = info.context.META.get("CONTENT_TYPE", "")
        if "multipart/form-data" in request_type:
            data.update(dict(info.context.FILES.items()))

        pk = data.pop("id")
        old_obj = get_Object_or_None(
            cls._meta.model, info, type='update', pk=pk)
        if not old_obj:
            return cls.get_errors(
                [
                    ErrorType(
                        field="id",
                        messages=[
                            f"A {cls._meta.model.__name__} obj with id: {pk} do not exist"
                        ],
                    )
                ]
            )

        nested_objs = cls.manage_nested_fields(data, root, info)
        serializer = cls._meta.serializer_class(
            old_obj,
            data=data,
            partial=True,
            context=info.context.user,
            **cls.get_serializer_kwargs(root, info, **kwargs),
        )

        ok, obj = cls.save(serializer, root, info)
        for m2m_field in m2m_dict:
            field = getattr(obj, m2m_field)
            field.set(m2m_dict[m2m_field])
        if not ok:
            return cls.get_errors(obj)
        elif nested_objs:
            [getattr(obj, field).add(*objs)
                for field, objs in nested_objs.items()]
        return cls.perform_mutate(obj, info)

    @classmethod
    def save(cls, serialized_obj, root, info, **kwargs):
        """
        graphene-django v3 now returns the full Enum object, instead of its value.
        We need to get its value before validating the submitted data.
        """
        for key in serialized_obj.initial_data:
            if "Enum" in type(serialized_obj.initial_data[key]).__name__:
                serialized_obj.initial_data[key] = serialized_obj.initial_data[
                    key
                ].value
        if serialized_obj.is_valid():
            try:
                obj = serialized_obj.save()
                return True, obj
            except Exception as e:
                # Format all raised exceptions as ErrorType
                # Field is `id` because it is required and we don't know what caused the exception
                # other than from the exception message
                errors = [
                    ErrorType(field="id", messages=[e.__str__()])
                ]
                # Atomic transaction support
                cls._set_errors_flag_to_context(info)
                return False, errors
        else:
            errors = [
                ErrorType(field=key, messages=value)
                for key, value in serialized_obj.errors.items()
            ]
            # Atomic transaction support
            cls._set_errors_flag_to_context(info)
            return False, errors

    @classmethod
    def CreateField(cls, *args, **kwargs):
        return Field(
            cls._meta.output,
            args=cls._meta.arguments["create"],
            resolver=cls.create,
            **kwargs,
        )

    @classmethod
    def DeleteField(cls, *args, **kwargs):
        return Field(
            cls._meta.output,
            args=cls._meta.arguments["delete"],
            resolver=cls.delete,
            **kwargs,
        )

    @classmethod
    def UpdateField(cls, *args, **kwargs):
        return Field(
            cls._meta.output,
            args=cls._meta.arguments["update"],
            resolver=cls.update,
            **kwargs,
        )

    @classmethod
    def MutationFields(cls, *args, **kwargs):
        create_field = cls.CreateField(*args, **kwargs)
        delete_field = cls.DeleteField(*args, **kwargs)
        update_field = cls.UpdateField(*args, **kwargs)

        return create_field, delete_field, update_field

    @staticmethod
    def _set_errors_flag_to_context(info):
        """
        Set MUTATION_ERRORS_FLAG to True in the context if there are errors.
        This will cause transactions to rollback on failure supporting atomic transactions.

        Source
        https://github.com/graphql-python/graphene-django/blob/623d0f219ebeaf2b11de4d7f79d84da8508197c8/graphene_django/forms/mutation.py#L189

        They only have it for forms, so we extend it for generic.
        """
        if info and info.context:
            setattr(info.context, MUTATION_ERRORS_FLAG, True)
