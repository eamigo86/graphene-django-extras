from collections import OrderedDict
from rest_framework import serializers
from graphene import ObjectType, Boolean, List, Field, Argument, InputObjectType, InputField, ID
from graphene.types.mutation import MutationOptions
from graphene.types.utils import yank_fields_from_attrs
from graphene.utils.deprecated import warn_deprecation
from graphene.utils.props import props
from graphene.utils.str_converters import to_camel_case
from .serializer_converter import SerializerEnumConverter
from graphene_django.registry import get_global_registry as gd_registry
from graphene_django_extras.registry import get_global_registry as gde_registry
from graphene_django.rest_framework.mutation import fields_for_serializer
from graphene_django.types import ErrorType, construct_fields, DjangoObjectType
from graphene_django_extras.base_types import factory_type
from graphene_django_extras.utils import get_Object_or_None
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

CREATE, UPDATE, DELETE = ('create', 'update', 'delete')

SerializerEnumConverter()


class BaseMutationOptions(MutationOptions):
    only_fields = ()
    exclude_fields = ()
    arguments_props = None
    convert_choices_to_enum = True


class SerializerMutationOptions(BaseMutationOptions):
    serializer_class = None


class BaseMutation(GraphqlPermissionMixin, MutationErrorHandler, ObjectType):
    lookup_field_description = None  # description for ID field
    lookup_field = None
    lookup_url_kwarg = None
    input_field_name = None
    input_type_name = None
    output_field_name = None
    output_field_description = None

    @classmethod
    def __init_subclass_with_meta__(
            cls,
            name=None,
            _meta=None,
            convert_choices_to_enum=True,
            **options
    ):
        name = name or '{}Response'.format(cls.__name__)
        assert _meta, "{} _meta instance is required".format(cls.__name__)

        model = getattr(_meta, "model", None)
        assert model, "model is missing in _meta - {}".format(cls.__name__)

        arguments_props = cls._get_argument_fields()

        _meta.arguments_props = arguments_props
        _meta.convert_choices_to_enum = convert_choices_to_enum

        super(BaseMutation, cls).__init_subclass_with_meta__(
            _meta=_meta, **options, name=name
        )

    class Meta:
        abstract = True

    ok = Boolean(description="Boolean field that return mutation result request.")
    errors = List(ErrorType, description="Errors list for the field")

    @classmethod
    def _get_update_input_type_name(cls):
        model = cls.get_model()
        default = to_camel_case("{}_Update_{}".format(cls.__name__, model._meta.model_name.capitalize()))
        return cls.input_type_name or default

    @classmethod
    def _get_create_input_type_name(cls):
        model = cls.get_model()
        default = to_camel_case("{}_Create_{}".format(cls.__name__, model._meta.model_name.capitalize()))
        return cls.input_type_name or default

    @classmethod
    def get_errors(cls, errors):
        extra_types = cls.get_extra_types(obj=None, info=None)
        errors_dict = {cls.output_field_name: None, "ok": False, "errors": errors}
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
        resp = {cls.output_field_name: obj, "ok": True, "errors": None}
        extra_types.update(resp)
        return cls(**extra_types)

    @classmethod
    def save(cls, serialized_obj, **kwargs):
        raise NotImplementedError('`save` method needs to be implemented'.format(cls.__name__))

    @classmethod
    def get_lookup_field_name(cls):
        model = cls.get_model()
        return cls.lookup_field or model._meta.pk.name

    @classmethod
    def get_model(cls):
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
        input_field_name = cls.input_field_name
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
    def _get_output_fields(cls, model, only_fields, exclude_fields):
        output_type = gd_registry().get_type_for_model(model) or gde_registry().get_type_for_model(model)
        if not output_type:
            factory_kwargs = {
                "model": model,
                'only_fields': only_fields,
                'exclude_fields': exclude_fields,
                'skip_registry': False,
                'description': cls.output_field_description
            }
            output_type = factory_type("output", DjangoObjectType, **factory_kwargs)

        output = Field(
            output_type,
            description=
            cls.output_field_description or "Result can `{}` or `Null` if any error message(s)".format(
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
        cls._action = CREATE
        input_fields = cls.base_args_setup()

        argument_type = type(
            cls._get_create_input_type_name(),
            (InputObjectType,),
            OrderedDict(
                input_fields
            ),
        )

        return cls._bundle_all_arguments(argument_type, input_fields=input_fields)

    @classmethod
    def _init_update_args(cls):
        cls._action = UPDATE
        input_fields = cls.base_args_setup()

        pk_name = cls.lookup_url_kwarg or cls.get_lookup_field_name()
        if not input_fields.get(pk_name) and not cls._meta.arguments_props.get(pk_name):
            input_fields.update({
                pk_name: Argument(
                    ID, required=True,
                    description=cls.lookup_field_description or "Django object unique identification field")
            })

        argument_type = type(
            cls._get_update_input_type_name(),
            (InputObjectType,),
            OrderedDict(
                input_fields
            ),
        )

        return cls._bundle_all_arguments(argument_type, input_fields=input_fields)

    @classmethod
    def _init_delete_args(cls):
        cls._action = DELETE
        pk_name = cls.lookup_url_kwarg or cls.get_lookup_field_name()
        input_fields = OrderedDict({
            pk_name: Argument(
                ID, required=True,
                description=cls.lookup_field_description or "Django object unique identification field")
        })

        argument = input_fields
        argument.update(cls._meta.arguments_props)
        return argument

    def __build_input_data(self, root, info, **kwargs):
        data = {}
        if self.input_field_name:
            data = kwargs.get(self.input_field_name)
        else:
            data.update(**kwargs)

        request_type = info.context.META.get("CONTENT_TYPE", "")
        if "multipart/form-data" in request_type:
            data.update({name: value for name, value in info.context.FILES.items()})
        return data

    def create(self, root, info, **kwargs):

        self.check_permissions(request=info.context)

        try:
            data = self.__build_input_data(root, info, **kwargs)

            obj = self.perform_create(root, info, data, **kwargs)
            assert obj is not None, (
                '`perform_create()` did not return an object instance.'
            )
            return self.perform_mutate(obj, info)
        except Exception as e:
            return self._handle_errors(e)

    def update(self, root, info, **kwargs):

        self.check_permissions(request=info.context)

        try:
            data = self.__build_input_data(root, info, **kwargs)

            existing_obj = self.get_object(root, info, data=data, **kwargs)

            if existing_obj:
                self.check_object_permissions(request=info.context, obj=existing_obj)
                obj = self.perform_update(root=root, info=info, data=data, instance=existing_obj, **kwargs)
                assert obj is not None, (
                    '`perform_update()` did not return an object instance.'
                )
                return self.perform_mutate(obj, info)

            else:
                pk = data.get(self.get_lookup_field_name())
                errors = self.construct_error(
                    field="id", message="A {} obj with id: {} do not exist".format(self.get_model().__name__, pk)
                )
                return self.get_errors(errors)
        except Exception as e:
            return self._handle_errors(e)

    def delete(self, root, info, **kwargs):

        self.check_permissions(request=info.context)

        try:
            pk = kwargs.get(self.get_lookup_field_name())
            data = self.__build_input_data(root, info, **kwargs)
            
            old_obj = self.get_object(root, info, data, **kwargs)

            if old_obj:
                self.check_object_permissions(request=info.context, obj=old_obj)
                self.perform_delete(info=info, obj=old_obj, **kwargs)
                if not old_obj.id:
                    old_obj.id = pk
                return self.perform_mutate(old_obj, info)
            else:
                errors = self.construct_error(
                    field="id", message="A {} obj with id: {} do not exist".format(
                        self.get_model().__name__, pk
                    )
                )
                return self.get_errors(errors)
        except Exception as e:
            return self._handle_errors(e)

    def get_object(self, root, info, data, **kwargs):
        look_up_field = self.get_lookup_field_name()
        lookup_url_kwarg = self.lookup_url_kwarg or look_up_field
        lookup_url_kwarg_value = data.get(lookup_url_kwarg) or kwargs.get(lookup_url_kwarg)
        filter_kwargs = {look_up_field: lookup_url_kwarg_value}
        return get_Object_or_None(self.get_model(), **filter_kwargs)

    @classmethod
    def resolver_wrapper(cls, resolver):
        def wrap(*args, **kwargs):
            instance = cls()
            instance._action = resolver.__name__
            resolver_func = getattr(instance, instance._action)
            return resolver_func(*args, **kwargs)
        return wrap


    @classmethod
    def Field(cls, args, name=None, description=None,
              deprecation_reason=None, required=False, resolver=None, **kwargs):
        """ Mount instance of mutation Field. """
        return Field(
            cls._meta.output,
            args=args,
            name=name,
            description=description or cls._meta.description,
            deprecation_reason=deprecation_reason,
            required=required,
            resolver=cls.resolver_wrapper(resolver),
            **kwargs
        )


class BaseSerializerMutation(BaseMutation):
    """
        Serializer Mutation Type Definition with Permission enabled
    """
    serializer_output_type_name = None  # only useful if `serializer_class_as_output = True`
    serializer_class_as_output = False

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
            cls,
            serializer_class=None,
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

        if not cls.serializer_output_type_name:
            cls.serializer_output_type_name = "{}Type".format(cls.__name__)

        output_field_name = cls.output_field_name or model._meta.model_name
        output_field = cls._get_output_type()
        django_fields = {output_field_name: None}

        if not output_field and not cls.serializer_class_as_output:
            django_fields[output_field_name] = cls._get_output_fields(
                model, only_fields, exclude_fields,
            )

        else:
            django_fields[output_field_name] = output_field if isinstance(output_field, Field) else Field(
                output_field, description=cls.output_field_description
            )

        if cls.serializer_class_as_output and not output_field:
            django_fields[output_field_name] = cls._get_output_from_serializer(
                serializer_class, only_fields, exclude_fields, convert_choices_to_enum
            )

        cls.output_field_name = output_field_name
        _meta = SerializerMutationOptions(cls)
        _meta.output = cls
        _meta.model = model
        _meta.fields = django_fields
        _meta.only_fields = only_fields
        _meta.exclude_fields = exclude_fields
        _meta.serializer_class = serializer_class

        super(BaseSerializerMutation, cls).__init_subclass_with_meta__(
            _meta=_meta, **options, description=description,
            convert_choices_to_enum=convert_choices_to_enum
        )

    @classmethod
    def save(cls, serialized_obj, **kwargs):
        serialized_obj.is_valid(raise_exception=True)
        obj = serialized_obj.save()
        return obj

    @classmethod
    def get_serializer_output_name(cls):
        return cls.serializer_output_type_name

    @classmethod
    def _get_output_from_serializer(
            cls, serializer_class, only_fields, exclude_fields, convert_choices_to_enum
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
            cls.output_field_description or "Result can `{}` or `Null` if any error message(s)".format(
                serializer_class.__name__)
        )
        return output

    def get_serializer(self):
        return self.__class__._meta.serializer_class

    @classmethod
    def base_args_setup(cls):
        serializer = cls().get_serializer()

        input_fields_from_serializer = fields_for_serializer(
            serializer(),
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
    def Field(cls, **kwargs):
        argument = cls._init_create_args()
        return super().Field(args=argument, resolver=cls.create, **kwargs)


class UpdateSerializerMutation(UpdateSerializerMixin, BaseSerializerMutation):
    class Meta:
        abstract = True

    @classmethod
    def Field(cls, **kwargs):
        argument = super()._init_update_args()
        return super().Field(args=argument, resolver=cls.update, **kwargs)


class DeleteSerializerMutation(DeleteModelMixin, BaseSerializerMutation):
    class Meta:
        abstract = True

    @classmethod
    def Field(cls, **kwargs):
        argument = cls._init_delete_args()
        return super().Field(resolver=cls.delete, args=argument, **kwargs)


class DRFSerializerMutation(CreateSerializerMixin, UpdateSerializerMixin,
                            DeleteModelMixin, BaseSerializerMutation):
    mutation_serializers = None

    @classmethod
    def __init_subclass_with_meta__(cls, serializer_class=None, **options):
        mutation_serializers = cls.mutation_serializers
        if cls.mutation_serializers is None:
            mutation_serializers = dict(
                {
                    'create': serializer_class,
                    'update': serializer_class
                }
            )

        assert isinstance(mutation_serializers, dict), (
            '`mutation_serializers` must be type of Dict - {}'.format(cls.__name__)
        )

        assert all(key in ['create', 'update'] for key in mutation_serializers.keys()), (
            '`mutation_serializers` can only take `create` or `update` as keys - {}'.format(cls.__name__)
        )

        assert all(issubclass(value, serializers.BaseSerializer) for value in mutation_serializers.values()), (
            'mutation_serializers `create` or `update` as value must be subclass of {} - {}'.format(
                serializers.BaseSerializer.__name__, cls.__name__
            )
        )
        cls.mutation_serializers = mutation_serializers
        super(DRFSerializerMutation, cls).__init_subclass_with_meta__(
            serializer_class=serializer_class, **options
        )

    class Meta:
        abstract = True

    def get_serializer(self):
        if hasattr(self, '_action'):
            serializer = self.mutation_serializers.get(self._action)
            return serializer or super(DRFSerializerMutation, self).get_serializer()
        return super(DRFSerializerMutation, self).get_serializer()

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
        update_field = cls.UpdateField(**kwargs)
        delete_field = cls.DeleteField(**kwargs)

        return create_field, update_field, delete_field


class ModelMutationOptions(BaseMutationOptions):
    model = None


class BaseModelMutation(BaseMutation):
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

        output_field_name = cls.output_field_name or model._meta.model_name
        django_fields = {
            output_field_name: output_field if isinstance(output_field, Field) else Field(
                output_field, description=cls.output_field_description
            )
        }

        if not output_field:
            django_fields[output_field_name] = cls._get_output_fields(
                model, only_fields, exclude_fields,
            )

        cls.output_field_name = output_field_name

        _meta = ModelMutationOptions(cls)
        _meta.output = cls
        _meta.model = model
        _meta.fields = django_fields
        _meta.only_fields = only_fields
        _meta.exclude_fields = exclude_fields

        super(BaseModelMutation, cls).__init_subclass_with_meta__(
            _meta=_meta, **options, description=description, convert_choices_to_enum=convert_choices_to_enum
        )

    @classmethod
    def _base_args_setup(cls, only_fields=None, exclude_fields=None):
        if only_fields or exclude_fields:
            factory_kwargs = [
                # model
                cls._meta.model,
                # register
                gd_registry(),
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

        if cls.input_field_name:
            raise Exception(
                '{} type can not be empty use `only_fields` or '
                '`exclude_fields` to defined its fields. {}'.format(cls.input_field_name, cls.__name__)
            )
        return OrderedDict()

    @classmethod
    def base_args_setup(cls):
        return cls._base_args_setup(cls._meta.only_fields, cls._meta.exclude_fields)

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
                          DeleteModelMixin, BaseModelMutation):
    """
    defined different mutation fields
    eg.
        create_fields = dict(
            only_fields=('a','b')
        )

        update_fields = dict(
            exclude_fields=('a', 'b')
        )

    Use either only_fields or exclude_fields
    """
    create_fields = None
    update_fields = None

    class Meta:
        abstract = True

    def create_mutate(self, info, data, **kwargs) -> object:
        """Creates the model and returns the created object"""
        raise NotImplementedError('`create_mutate` method needs to be implemented'.format(self.__class__.__name__))

    def update_mutate(self, info, data, instance, **kwargs) -> object:
        """Updates a model and returns the updated object"""
        raise NotImplementedError('`update_mutate` method needs to be implemented'.format(self.__class__.__name__))

    @classmethod
    def base_args_setup(cls):
        only_fields, exclude_fields = None, None
        if hasattr(cls, '_action'):
            action_fields: dict = getattr(cls, f'{cls._action}_fields')

            if action_fields:
                assert isinstance(action_fields, dict), (
                    f'`{cls._action}_fields` must be a dict type - {cls.__name__} '
                )

                assert all(key in ['only_fields', 'exclude_fields'] for key in action_fields.keys()), (
                    f'`{cls._action}_fields` can only take `only_fields` or `only_fields` as keys - {cls.__name__}'
                )

                assert all(isinstance(value, (list, tuple)) for value in action_fields.values()), (
                    f'`{cls._action}_fields` can only take `list` or `tuples` as type - {cls.__name__}'
                )

                assert not (action_fields.get('only_fields') and action_fields.get('exclude_fields')), (
                    f"Cannot set both 'only_fields' and 'exclude_fields' options on "
                    f"{cls._action}_fields"
                )

                only_fields, exclude_fields = action_fields.get('only_fields'), action_fields.get('exclude_fields')

        return cls._base_args_setup(
            only_fields or cls._meta.only_fields, exclude_fields or cls._meta.exclude_fields
        )

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
        update_field = cls.UpdateField(**kwargs)
        delete_field = cls.DeleteField(**kwargs)

        return create_field, update_field, delete_field
