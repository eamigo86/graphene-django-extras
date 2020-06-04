from collections import OrderedDict
from graphene import ObjectType, Boolean, List, Field, Argument, InputObjectType, InputField, ID
from graphene.types.mutation import MutationOptions
from graphene.types.utils import yank_fields_from_attrs
from graphene.utils.deprecated import warn_deprecation
from graphene.utils.props import props
from graphene.utils.str_converters import to_camel_case
from .serializer_converter import SerializerEnumConverter
from graphene_django.registry import get_global_registry
from graphene_django.rest_framework.mutation import fields_for_serializer
from graphene_django.types import ErrorType, DjangoObjectType, construct_fields
from graphene_django_extras.base_types import factory_type
from graphene_django_extras.rest_framework.mixins import *

__all__ = (
    "BaseMutationOptions",
    "BaseMutation",
    "BaseSerializerMutation",
    "CreateSerializerMutation",
    "UpdateSerializerMutation",
    "DeleteSerializerMutation",
    "DRFSerializerMutation",
    "BaseModelMutation",
    "UpdateModelMutation",
    "DeleteModelMutation",
    "CreateModelMutation",
    "DjangoModelMutation",
)
SerializerEnumConverter()


class BaseMutationOptions(MutationOptions):
    only_fields = ()
    exclude_fields = ()
    input_field_name = None
    output_field_name = None
    output_field_description = None
    convert_choices_to_enum = True
    update_input_type_name = None
    create_input_type_name = None
    arguments_props = None


class SerializerMutationOptions(BaseMutationOptions):
    serializer_class = None
    serializer_class_as_output = False


class BaseMutation(ObjectType):
    lookup_field_description = None  # description for ID field
    lookup_field = None
    lookup_url_kwarg = None

    @classmethod
    def __init_subclass_with_meta__(
            cls, # description for ID field
            input_field_name=None,
            convert_choices_to_enum=True,
            update_input_type_name=None,
            create_input_type_name=None,
            name=None,
            _meta=None,
            **options
    ):
        name = name or '{}Response'.format(cls.__name__)
        assert _meta, "{} _meta instance is required".format(cls.__name__)

        model = getattr(_meta, "model", None)
        assert model, "model is missing in _meta - {}".format(cls.__name__)

        arguments_props = cls._get_argument_fields()

        _meta.input_field_name = input_field_name
        _meta.convert_choices_to_enum = convert_choices_to_enum
        _meta.arguments_props = arguments_props
        _meta.update_input_type_name = update_input_type_name
        _meta.create_input_type_name = create_input_type_name

        super(BaseMutation, cls).__init_subclass_with_meta__(
            _meta=_meta, **options, name=name
        )

    class Meta:
        abstract = True

    ok = Boolean(description="Boolean field that return mutation result request.")
    errors = List(ErrorType, description="Errors list for the field")

    @classmethod
    def get_update_input_type_name(cls):
        model = cls._get_model()
        default = to_camel_case("{}_Update_{}".format(cls.__name__, model._meta.model_name.capitalize()))
        return cls._meta.update_input_type_name or default

    @classmethod
    def get_create_input_type_name(cls):
        model = cls._get_model()
        default = to_camel_case("{}_Create_{}".format(cls.__name__, model._meta.model_name.capitalize()))
        return cls._meta.create_input_type_name or default

    @classmethod
    def error_builder(cls, serialized_obj):
        errors = [
            ErrorType(field=key, messages=value)
            for key, value in serialized_obj.errors.items()
        ]
        return errors

    @classmethod
    def get_errors(cls, errors):
        extra_types = cls.get_extra_types(obj=None, info=None)
        errors_dict = {cls._meta.output_field_name: None, "ok": False, "errors": errors}
        extra_types.update(errors_dict)
        return cls(**extra_types)

    @classmethod
    def get_extra_types(cls, obj, info):
        """
        define values for any extra types provided on your mutation class
        :param obj: Object
        :param info: graphene info instance
        :return: `Dict()`
        """
        return dict()

    @classmethod
    def perform_mutate(cls, obj, info):
        extra_types = cls.get_extra_types(obj, info)
        resp = {cls._meta.output_field_name: obj, "ok": True, "errors": None}
        extra_types.update(resp)
        return cls(**extra_types)

    @classmethod
    def save(cls, serialized_obj, **kwargs):
        raise NotImplementedError('`save` method needs to be implemented'.format(cls.__name__))

    @classmethod
    def get_lookup_field_name(cls):
        model = cls._get_model()
        return cls.lookup_field or model._meta.pk.name

    @classmethod
    def _get_model(cls):
        model = cls._meta.model
        return model

    @classmethod
    def _get_output_type(cls):
        output_field = getattr(cls, "Output", None)
        if output_field:
            delattr(cls, "Output")
        return output_field

    @classmethod
    def _bundle_all_arguments(cls, args_type, input_fields):
        input_field_name = cls._meta.input_field_name
        if input_field_name:
            arguments = OrderedDict({input_field_name: Argument(args_type, required=True)})
            arguments.update(cls._meta.arguments_props)
            return arguments

        argument = OrderedDict(
            {
                i: Argument(type=t.type, description=t.description, name=t.name, required=getattr(t, 'required', None))
                for i, t in input_fields.items()
            }
        )

        argument.update(cls._meta.arguments_props)
        return argument

    @classmethod
    def _get_output_fields(cls, model, output_field_description):
        output_type = get_global_registry().get_type_for_model(model)
        if not output_type:
            factory_kwargs = {
                "model": model,
                'fields': (),
                'exclude': (),
            }
            output_type = factory_type("output", DjangoObjectType, **factory_kwargs)

        output = Field(
            output_type,
            description=
            output_field_description or "Result can `{}` or `Null` if any error message(s)".format(
                model._meta.model_name.capitalize())
        )
        return output

    @classmethod
    def _get_argument_fields(cls):
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
        arguments_props = {}
        if input_class:
            arguments_props = props(input_class)
        return arguments_props

    @classmethod
    def base_args_setup(cls):
        raise NotImplementedError('`base_args_setup` needs to be implemented'.format(cls.__name__))

    @classmethod
    def _init_create_args(cls):
        input_fields = cls.base_args_setup()

        argument_type = type(
            cls.get_create_input_type_name(),
            (InputObjectType,),
            OrderedDict(
                input_fields
            ),
        )
        return cls._bundle_all_arguments(argument_type, input_fields=input_fields)

    @classmethod
    def _init_update_args(cls):
        input_fields = cls.base_args_setup()

        pk_name = cls.lookup_url_kwarg or cls.get_lookup_field_name()
        if not input_fields.get(pk_name) and not cls._meta.arguments_props.get(pk_name):
            input_fields.update({
                pk_name: Argument(
                    ID, required=True,
                    description=cls.lookup_field_description or "Django object unique identification field")
            })

        argument_type = type(
            cls.get_update_input_type_name(),
            (InputObjectType,),
            OrderedDict(
                input_fields
            ),
        )

        return cls._bundle_all_arguments(argument_type, input_fields=input_fields)

    @classmethod
    def _init_delete_args(cls):
        pk_name = cls.lookup_url_kwarg or cls.get_lookup_field_name()
        input_fields = OrderedDict({
            pk_name: Argument(
                ID, required=True,
                description=cls.lookup_field_description or "Django object unique identification field")
        })

        argument = input_fields
        return argument

    @classmethod
    def Field(cls, args, name=None, description=None, deprecation_reason=None, required=False, **kwargs):
        """ Mount instance of mutation Field. """
        return Field(
            cls._meta.output,
            args=args,
            name=name,
            description=description or cls._meta.description,
            deprecation_reason=deprecation_reason,
            required=required,
            **kwargs
        )


class BaseSerializerMutation(GraphqlPermissionMixin, BaseMutation):
    """
        Serializer Mutation Type Definition with Permission enabled
    """

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
            cls,
            serializer_class=None,
            output_field_name=None,
            output_field_description=None,
            serializer_class_as_output=False,
            only_fields=(),
            exclude_fields=(),
            convert_choices_to_enum=True,
            description=None,
            **options
    ):
        if not serializer_class:
            raise Exception(
                "serializer_class is required on all DjangoSerializerMutation"
            )

        model = serializer_class.Meta.model

        description = description or "SerializerMutation for {} model".format(
            model.__name__
        )

        output_field_name = output_field_name or model._meta.model_name
        output_field = cls._get_output_type()
        django_fields = {output_field_name: None}
        if not output_field and not serializer_class_as_output:
            django_fields[output_field_name] = cls._get_output_fields(
                model, output_field_description
            )
        else:
            django_fields[output_field_name] = output_field if isinstance(output_field, Field) else Field(
                output_field, description=output_field_description
            )

        if serializer_class_as_output and not output_field:
            django_fields[output_field_name] = cls._get_output_from_serializer(
                serializer_class, only_fields, exclude_fields,
                convert_choices_to_enum, output_field_description
            )

        _meta = SerializerMutationOptions(cls)
        _meta.output = cls
        _meta.model = model
        _meta.fields = django_fields
        _meta.only_fields = only_fields
        _meta.exclude_fields = exclude_fields
        _meta.serializer_class = serializer_class
        _meta.output_field_name = output_field_name
        _meta.output_field_description = output_field_description

        super(BaseSerializerMutation, cls).__init_subclass_with_meta__(
            _meta=_meta, **options, description=description, serializer_class_as_output=serializer_class_as_output,
            convert_choices_to_enum=convert_choices_to_enum)

    @classmethod
    def save(cls, serialized_obj, **kwargs):
        serialized_obj.is_valid(raise_exception=True)
        obj = serialized_obj.save()
        return obj

    @classmethod
    def get_serializer_output_name(cls):
        return None

    @classmethod
    def _get_output_from_serializer(
            cls, serializer_class, only_fields, exclude_fields,
            convert_choices_to_enum, output_field_description
    ):
        serializer = serializer_class()
        output_fields = fields_for_serializer(
            serializer,
            only_fields=only_fields,
            exclude_fields=exclude_fields,
            is_input=False,
            convert_choices_to_enum=convert_choices_to_enum,
        )

        output_type = type(
            cls.get_serializer_output_name() or "{}".format(serializer_class.__name__),
            (ObjectType,),
            OrderedDict(
                output_fields
            ),
        )

        output = Field(
            output_type,
            description=
            output_field_description or "Result can `{}` or `Null` if any error message(s)".format(
                serializer_class.__name__)
        )
        return output

    @classmethod
    def get_serializer(cls):
        return cls._meta.serializer_class

    @classmethod
    def base_args_setup(cls):
        serializer = cls._meta.serializer_class()

        input_fields_from_serializer = fields_for_serializer(
            serializer,
            only_fields=cls._meta.only_fields,
            exclude_fields=cls._meta.exclude_fields,
            is_input=True,
            convert_choices_to_enum=cls._meta.convert_choices_to_enum,
        )
        input_fields = yank_fields_from_attrs(input_fields_from_serializer, _as=InputField, sort=False)
        return input_fields


class CreateSerializerMutation(CreateSerializerMixin, BaseSerializerMutation):
    class Meta:
        abstract = True

    @classmethod
    def get_serializer_output_name(cls):
        return "{}Type".format(cls.__name__)

    @classmethod
    def Field(cls, **kwargs):
        argument = cls._init_create_args()
        return super().Field(args=argument, resolver=cls.create, **kwargs)


class UpdateSerializerMutation(UpdateSerializerMixin, BaseSerializerMutation):
    class Meta:
        abstract = True

    @classmethod
    def get_serializer_output_name(cls):
        return "{}Type".format(cls.__name__)

    @classmethod
    def Field(cls, **kwargs):
        argument = super()._init_update_args()
        return super().Field(args=argument, resolver=cls.update, **kwargs)


class DeleteSerializerMutation(DeleteModelMixin, BaseSerializerMutation):
    class Meta:
        abstract = True

    @classmethod
    def get_serializer_output_name(cls):
        return "{}Type".format(cls.__name__)

    @classmethod
    def Field(cls, **kwargs):
        argument = cls._init_delete_args()
        return super().Field(resolver=cls.delete, args=argument, **kwargs)


class DRFSerializerMutation(CreateSerializerMixin, UpdateSerializerMixin,
                            DeleteModelMixin, BaseSerializerMutation):
    class Meta:
        abstract = True

    @classmethod
    def CreateField(cls, **kwargs):
        argument = cls._init_create_args()
        return super().Field(args=argument, resolver=cls.create, **kwargs)

    @classmethod
    def DeleteField(cls, **kwargs):
        argument = cls._init_delete_args()
        return super().Field(resolver=cls.delete, args=argument, **kwargs)

    @classmethod
    def UpdateField(cls, **kwargs):
        argument = super()._init_update_args()
        return super().Field(args=argument, resolver=cls.update, **kwargs)

    @classmethod
    def MutationFields(cls, **kwargs):
        create_field = cls.CreateField(**kwargs)
        delete_field = cls.DeleteField(**kwargs)
        update_field = cls.UpdateField(**kwargs)

        return create_field, delete_field, update_field


class ModelMutationOptions(BaseMutationOptions):
    model = None


class BaseModelMutation(GraphqlPermissionMixin, BaseMutation):
    """
    Serializer Mutation Type Definition with Permission enabled
    """

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
            cls,
            only_fields=(),
            exclude_fields=(),
            model=None,
            output_field_name=None,
            output_field_description=None,
            description="",
            convert_choices_to_enum=True,
            **options
    ):

        if not model:
            raise Exception(
                "model is required on all DjangoModelMutation"
            )

        description = description or "Model Mutation for {} model".format(
            model.__name__
        )
        output_field = cls._get_output_type()

        output_field_name = output_field_name or model._meta.model_name
        django_fields = {
            output_field_name: output_field if isinstance(output_field, Field) else Field(
                output_field, description=output_field_description
            )
        }

        if not output_field:
            django_fields[output_field_name] = cls._get_output_fields(model, output_field_description)

        _meta = ModelMutationOptions(cls)
        _meta.output = cls
        _meta.model = model
        _meta.fields = django_fields
        _meta.output_field_name = output_field_name
        _meta.only_fields = only_fields
        _meta.exclude_fields = exclude_fields
        _meta.output_field_description = output_field_description
        _meta.output_field_name = output_field_name
        _meta.convert_choices_to_enum = convert_choices_to_enum

        super(BaseModelMutation, cls).__init_subclass_with_meta__(
            _meta=_meta, **options, description=description
        )

    @classmethod
    def base_args_setup(cls):
        if cls._meta.only_fields or cls._meta.exclude_fields:
            factory_kwargs = [
                # model
                cls._meta.model,
                # register
                get_global_registry(),
                # fields
                cls._meta.only_fields,
                # exclude
                cls._meta.exclude_fields,
                # convert_choices_to_enum
                cls._meta.convert_choices_to_enum,
            ]
            django_fields = yank_fields_from_attrs(
                construct_fields(*factory_kwargs),
                _as=InputField,
            )
            return django_fields

        if cls._meta.input_field_name:
            raise Exception(
                '{} type can not be empty use `only_fields` or '
                '`exclude_fields` to defined its fields. {}'.format(cls._meta.input_field_name, cls.__name__)
            )
        return OrderedDict()

    @classmethod
    def save(cls, serialized_obj, **kwargs):
        pass


class UpdateModelMutation(UpdateModelMixin, BaseModelMutation):
    def update_mutate(self, info, data, instance, **kwargs):
        """Updates a model and returns the updated object"""
        raise NotImplementedError('`update_mutate` method needs to be implemented'.format(self.__class__.__name__))

    class Meta:
        abstract = True

    @classmethod
    def Field(cls, **kwargs):
        argument = super()._init_update_args()
        return super().Field(args=argument, resolver=cls.update, **kwargs)


class DeleteModelMutation(DeleteModelMixin, BaseModelMutation):
    class Meta:
        abstract = True

    @classmethod
    def Field(cls, **kwargs):
        argument = cls._init_delete_args()
        return super().Field(resolver=cls.delete, args=argument, **kwargs)


class CreateModelMutation(CreateModelMixin, BaseModelMutation):
    def create_mutate(self, info, data, **kwargs):
        """Creates the model and returns the created object"""
        raise NotImplementedError('`create_mutate` method needs to be implemented'.format(self.__class__.__name__))

    class Meta:
        abstract = True

    @classmethod
    def Field(cls, **kwargs):
        argument = cls._init_create_args()
        return super().Field(args=argument, resolver=cls.create, **kwargs)


class DjangoModelMutation(CreateModelMixin, UpdateModelMixin,
                          DeleteModelMixin, BaseSerializerMutation):
    class Meta:
        abstract = True

    def create_mutate(self, info, data, **kwargs) -> object:
        """Creates the model and returns the created object"""
        raise NotImplementedError('`create_mutate` method needs to be implemented'.format(self.__class__.__name__))

    def update_mutate(self, info, data, instance, **kwargs) -> object:
        """Updates a model and returns the updated object"""
        raise NotImplementedError('`update_mutate` method needs to be implemented'.format(self.__class__.__name__))

    @classmethod
    def CreateField(cls, **kwargs):
        argument = cls._init_create_args()
        return super().Field(args=argument, resolver=cls.create, **kwargs)

    @classmethod
    def DeleteField(cls, **kwargs):
        argument = cls._init_delete_args()
        return super().Field(resolver=cls.delete, args=argument, **kwargs)

    @classmethod
    def UpdateField(cls, **kwargs):
        argument = super()._init_update_args()
        return super().Field(args=argument, resolver=cls.update, **kwargs)

    @classmethod
    def MutationFields(cls, **kwargs):
        create_field = cls.CreateField(**kwargs)
        delete_field = cls.DeleteField(**kwargs)
        update_field = cls.UpdateField(**kwargs)

        return create_field, delete_field, update_field
