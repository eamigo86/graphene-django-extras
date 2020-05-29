from graphene_django.converter import convert_choices_to_named_enum_with_descriptions
from graphene_django.rest_framework.serializer_converter import get_graphene_type_from_serializer_field
from graphene_django.utils import get_model_fields
from rest_framework import serializers
from graphene_django.registry import get_global_registry
__all__ = ['SerializerEnumConverter']


class SerializerEnumConverter:
    """
    fix for enum types for the same serializer field
    """
    serializers_enum_types_cache = {}

    @staticmethod
    @get_graphene_type_from_serializer_field.register(serializers.ChoiceField)
    def convert_serializer_field_to_enum(field):
        # enums require a name
        register = get_global_registry()
        enum_name, cache_name = SerializerEnumConverter.get_cache_name_enum_name(field)
        registered_field = register.get_converted_field(cache_name)
        if registered_field:
            return registered_field.get_type()
        cached_type = SerializerEnumConverter.serializers_enum_types_cache.get(str(cache_name), None)
        if cached_type:
            return cached_type
        ret_type = convert_choices_to_named_enum_with_descriptions(enum_name, field.choices)
        SerializerEnumConverter.serializers_enum_types_cache[str(cache_name)] = ret_type
        return ret_type

    @staticmethod
    def get_cache_name_enum_name(field):
        name = field.field_name or field.source or "Choices"
        serializer = field.parent
        if isinstance(serializer, serializers.ModelSerializer):
            _model_fields = dict(get_model_fields(serializer.Meta.model))
            _model_field = _model_fields.get(name)
            enum_name = f'{serializer.Meta.model.__name__}{name.capitalize()}'
            return enum_name, _model_field
        cache_name = "{}_{}".format(serializer.__class__.__name__, name)
        enum_name = f'{serializer.__class__.__name__}{name}'
        return enum_name, cache_name
