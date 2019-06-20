# -*- coding: utf-8 -*-
from collections import OrderedDict

from graphene import Boolean, List, Field, ID, Argument, ObjectType
from graphene.types.base import BaseOptions
from graphene.utils.deprecated import warn_deprecation
from graphene.utils.props import props
from graphene_django.types import ErrorType

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

    ok = Boolean(description="Boolean field that return mutation result request.")
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

        if not serializer_class:
            raise Exception(
                "serializer_class is required on all DjangoSerializerMutation"
            )

        model = serializer_class.Meta.model

        description = description or "SerializerMutation for {} model".format(
            model.__name__
        )

        input_field_name = input_field_name or "new_{}".format(model._meta.model_name)
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
        if input_class:
            arguments = props(input_class)
        else:
            arguments = {}

        registry = get_global_registry()

        factory_kwargs = {
            "model": model,
            "only_fields": only_fields,
            "include_fields": include_fields,
            "exclude_fields": exclude_fields,
            "nested_fields": nested_fields,
            "registry": registry,
            "skip_registry": False,
        }

        output_type = registry.get_type_for_model(model)

        if not output_type:
            output_type = factory_type("output", DjangoObjectType, **factory_kwargs)

        django_fields = OrderedDict({output_field_name: Field(output_type)})

        global_arguments = {}
        for operation in ("create", "delete", "update"):
            global_arguments.update({operation: OrderedDict()})

            if operation != "delete":
                input_type = registry.get_type_for_model(model, for_input=operation)

                if not input_type:
                    # factory_kwargs.update({'skip_registry': True})
                    input_type = factory_type(
                        "input", DjangoInputObjectType, operation, **factory_kwargs
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
        _meta.input_field_name = input_field_name
        _meta.output_field_name = output_field_name
        _meta.nested_fields = nested_fields

        super(DjangoSerializerMutation, cls).__init_subclass_with_meta__(
            _meta=_meta, description=description, **options
        )

    @classmethod
    def get_errors(cls, errors):
        errors_dict = {cls._meta.output_field_name: None, "ok": False, "errors": errors}

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
                sub_data = data.pop(field, None)
                if sub_data:
                    serialized_data = cls._meta.nested_fields[field](
                        data=sub_data, many=True if type(sub_data) == list else False
                    )
                    ok, result = cls.save(serialized_data, root, info)
                    if not ok:
                        return cls.get_errors(result)
                    if type(sub_data) == list:
                        nested_objs.update({field: result})
                    else:
                        data.update({field: result.id})
        return nested_objs

    @classmethod
    def create(cls, root, info, **kwargs):
        data = kwargs.get(cls._meta.input_field_name)
        request_type = info.context.META.get("CONTENT_TYPE", "")
        if "multipart/form-data" in request_type:
            data.update({name: value for name, value in info.context.FILES.items()})

        nested_objs = cls.manage_nested_fields(data, root, info)
        serializer = cls._meta.serializer_class(
            data=data, **cls.get_serializer_kwargs(root, info, **kwargs)
        )

        ok, obj = cls.save(serializer, root, info)
        if not ok:
            return cls.get_errors(obj)
        elif nested_objs:
            [getattr(obj, field).add(*objs) for field, objs in nested_objs.items()]
        return cls.perform_mutate(obj, info)

    @classmethod
    def delete(cls, root, info, **kwargs):
        pk = kwargs.get("id")

        old_obj = get_Object_or_None(cls._meta.model, pk=pk)
        if old_obj:
            old_obj.delete()
            old_obj.id = pk
            return cls.perform_mutate(old_obj, info)
        else:
            return cls.get_errors(
                [
                    ErrorType(
                        field="id",
                        messages=[
                            "A {} obj with id {} do not exist".format(
                                cls._meta.model.__name__, pk
                            )
                        ],
                    )
                ]
            )

    @classmethod
    def update(cls, root, info, **kwargs):
        data = kwargs.get(cls._meta.input_field_name)
        request_type = info.context.META.get("CONTENT_TYPE", "")
        if "multipart/form-data" in request_type:
            data.update({name: value for name, value in info.context.FILES.items()})

        pk = data.pop("id")
        old_obj = get_Object_or_None(cls._meta.model, pk=pk)
        if old_obj:
            nested_objs = cls.manage_nested_fields(data, root, info)
            serializer = cls._meta.serializer_class(
                old_obj,
                data=data,
                partial=True,
                **cls.get_serializer_kwargs(root, info, **kwargs),
            )

            ok, obj = cls.save(serializer, root, info)
            if not ok:
                return cls.get_errors(obj)
            elif nested_objs:
                [getattr(obj, field).add(*objs) for field, objs in nested_objs.items()]
            return cls.perform_mutate(obj, info)
        else:
            return cls.get_errors(
                [
                    ErrorType(
                        field="id",
                        messages=[
                            "A {} obj with id: {} do not exist".format(
                                cls._meta.model.__name__, pk
                            )
                        ],
                    )
                ]
            )

    @classmethod
    def save(cls, serialized_obj, root, info, **kwargs):
        if serialized_obj.is_valid():
            obj = serialized_obj.save()
            return True, obj

        else:
            errors = [
                ErrorType(field=key, messages=value)
                for key, value in serialized_obj.errors.items()
            ]
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
