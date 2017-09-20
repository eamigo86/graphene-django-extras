# -*- coding: utf-8 -*-
import re
from collections import OrderedDict

from django.contrib.postgres.fields import ArrayField, HStoreField, RangeField
from django.db import models
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from graphene import (Field, ID, Boolean, Dynamic, Enum, Float, Int, List, NonNull, String, UUID)
from graphene.types.datetime import DateTime, Time
from graphene.types.json import JSONString
from graphene.utils.str_converters import to_camel_case, to_const
from graphene_django.utils import import_single_dispatch, get_model_fields, get_related_model
from rest_framework.fields import JSONField

from .fields import DjangoFilterListField
from .fields import DjangoListField

singledispatch = import_single_dispatch()


NAME_PATTERN = r'^[_a-zA-Z][_a-zA-Z0-9]*$'
COMPILED_NAME_PATTERN = re.compile(NAME_PATTERN)


def assert_valid_name(name):
    """Helper to assert that provided names are valid."""
    assert COMPILED_NAME_PATTERN.match(name), 'Names must match /{}/ but "{}" does not.'.format(NAME_PATTERN, name)


def convert_choice_name(name):
    name = to_const(force_text(name))
    try:
        assert_valid_name(name)
    except AssertionError:
        name = "A_%s" % name
    return name


def get_choices(choices):
    converted_names = []
    for value, help_text in choices:
        if isinstance(help_text, (tuple, list)):
            for choice in get_choices(help_text):
                yield choice
        else:
            name = convert_choice_name(value)
            while name in converted_names:
                name += '_' + str(len(converted_names))
            converted_names.append(name)
            description = help_text
            yield name, value, description


def convert_django_field_with_choices(field, registry=None, input_flag=None):
    choices = getattr(field, 'choices', None)
    if choices:
        meta = field.model._meta

        name = to_camel_case('{}_{}_{}'.format(meta.object_name, field.name, 'Input')) \
            if input_flag \
            else to_camel_case('{}_{}'.format(meta.object_name, field.name))

        choices = list(get_choices(choices))
        named_choices = [(c[0], c[1]) for c in choices]
        named_choices_descriptions = {c[0]: c[2] for c in choices}

        class EnumWithDescriptionsType(object):
            @property
            def description(self):
                return named_choices_descriptions[self.name]

        enum = Enum(name, list(named_choices), type=EnumWithDescriptionsType)
        return enum(description=field.help_text, required=not field.null and input_flag == 'create')
    return convert_django_field(field, registry, input_flag)


def construct_fields(model, registry, only_fields, exclude_fields, input_flag=None):
    _model_fields = get_model_fields(model)

    fields = OrderedDict()

    if input_flag == 'delete':
        converted = convert_django_field_with_choices(dict(_model_fields)['id'], registry)
        fields['id'] = converted
    else:
        for name, field in _model_fields:
            if input_flag == 'create' and name == 'id':
                continue

            is_not_in_only = only_fields and name not in only_fields
            # is_already_created = name in options.fields
            is_excluded = name in exclude_fields  # or is_already_created
            # https://docs.djangoproject.com/en/1.10/ref/models/fields/#django.db.models.ForeignKey.related_query_name
            is_no_backref = str(name).endswith('+')
            if is_not_in_only or is_excluded or is_no_backref:
                # We skip this field if we specify only_fields and is not
                # in there. Or when we exclude this field in exclude_fields.
                # Or when there is no back reference.
                continue
            converted = convert_django_field_with_choices(field, registry, input_flag)

            fields[name] = converted

    return fields


@singledispatch
def convert_django_field(field, registry=None, input_flag=None):
    raise Exception(
        "Don't know how to convert the Django field %s (%s)" %
        (field, field.__class__))


@convert_django_field.register(models.CharField)
@convert_django_field.register(models.TextField)
@convert_django_field.register(models.EmailField)
@convert_django_field.register(models.SlugField)
@convert_django_field.register(models.URLField)
@convert_django_field.register(models.GenericIPAddressField)
@convert_django_field.register(models.FileField)
def convert_field_to_string(field, registry=None, input_flag=None):
    return String(description=field.help_text, required=not field.null and input_flag == 'create')


@convert_django_field.register(models.AutoField)
def convert_field_to_id(field, registry=None, input_flag=None):
    if input_flag:
        return ID(description=field.help_text or _('Django object unique identification field'),
                  required=input_flag == 'update')
    return ID(description=field.help_text or _('Django object unique identification field'), required=not field.null)


@convert_django_field.register(models.UUIDField)
def convert_field_to_uuid(field, registry=None, input_flag=None):
    return UUID(description=field.help_text, required=not field.null and input_flag == 'create')


@convert_django_field.register(models.PositiveIntegerField)
@convert_django_field.register(models.PositiveSmallIntegerField)
@convert_django_field.register(models.SmallIntegerField)
@convert_django_field.register(models.BigIntegerField)
@convert_django_field.register(models.IntegerField)
def convert_field_to_int(field, registry=None, input_flag=None):
    return Int(description=field.help_text, required=not field.null and input_flag == 'create')


@convert_django_field.register(models.BooleanField)
def convert_field_to_boolean(field, registry=None, input_flag=None):
    return NonNull(Boolean, description=field.help_text)


@convert_django_field.register(models.NullBooleanField)
def convert_field_to_nullboolean(field, registry=None, input_flag=None):
    return Boolean(description=field.help_text, required=not field.null and input_flag == 'create')


@convert_django_field.register(models.DecimalField)
@convert_django_field.register(models.FloatField)
@convert_django_field.register(models.DurationField)
def convert_field_to_float(field, registry=None, input_flag=None):
    return Float(description=field.help_text, required=not field.null and input_flag == 'create')


@convert_django_field.register(models.DateField)
def convert_date_to_string(field, registry=None, input_flag=None):
    return DateTime(description=field.help_text, required=not field.null and input_flag == 'create')


@convert_django_field.register(models.TimeField)
def convert_time_to_string(field, registry=None, input_flag=False):
    return Time(description=field.help_text, required=not field.null and input_flag == 'create')


@convert_django_field.register(models.OneToOneRel)
def convert_onetoone_field_to_djangomodel(field, registry=None, input_flag=None):
    model = get_related_model(field)

    def dynamic_type():
        if input_flag:
            return ID(description=field.help_text, required=input_flag == 'create')

        _type = registry.get_type_for_model(model)
        if not _type:
            return

        # We do this for a bug in Django 1.8, where null attr
        # is not available in the OneToOneRel instance
        # null = getattr(field, 'null', True)
        # return Field(_type, required=not null)

        return Field(_type)

    return Dynamic(dynamic_type)


@convert_django_field.register(models.ManyToManyField)
def convert_field_to_list_or_connection(field, registry=None, input_flag=None):
    model = get_related_model(field)

    def dynamic_type():
        if input_flag:
            return DjangoListField(ID, required=not field.blank and input_flag == 'create')

        _type = registry.get_type_for_model(model)
        if not _type:
            return

        if _type._meta.filter_fields:
            return DjangoFilterListField(_type)
            # return DjangoFilterPaginateListField(_type, pagination=LimitOffsetGraphqlPagination())
        return DjangoListField(_type)

    return Dynamic(dynamic_type)


@convert_django_field.register(models.ManyToManyRel)
@convert_django_field.register(models.ManyToOneRel)
def convert_many_rel_to_djangomodel(field, registry=None, input_flag=None):
    model = get_related_model(field)
    if isinstance(field, models.ManyToManyRel):
        for f in field.related_model._meta.many_to_many:
            if f.rel.name == field.name and f.rel.model == field.model:
                blank = f.blank
    else:
        blank = True

    def dynamic_type():
        if input_flag:
            return DjangoListField(ID, required=not blank and input_flag == 'create')

        _type = registry.get_type_for_model(model)
        if not _type:
            return

        if _type._meta.filter_fields:
            return DjangoFilterListField(_type)
            # return DjangoFilterPaginateListField(_type, pagination=LimitOffsetGraphqlPagination())
        return DjangoListField(_type)

    return Dynamic(dynamic_type)


@convert_django_field.register(models.OneToOneField)
@convert_django_field.register(models.ForeignKey)
def convert_field_to_djangomodel(field, registry=None, input_flag=None):
    model = get_related_model(field)

    def dynamic_type():
        if input_flag:
            return ID(description=field.help_text, required=input_flag == 'create')

        _type = registry.get_type_for_model(model)
        if not _type:
            return

        # return Field(_type, description=field.help_text, required=field.null)
        return Field(_type, description=field.help_text)

    return Dynamic(dynamic_type)


@convert_django_field.register(ArrayField)
def convert_postgres_array_to_list(field, registry=None, input_flag=None):
    base_type = convert_django_field(field.base_field)
    if not isinstance(base_type, (List, NonNull)):
        base_type = type(base_type)
    return List(base_type, description=field.help_text, required=not field.null and input_flag == 'create')


@convert_django_field.register(HStoreField)
@convert_django_field.register(JSONField)
def convert_posgres_field_to_string(field, registry=None, input_flag=None):
    return JSONString(description=field.help_text, required=not field.null and input_flag == 'create')


@convert_django_field.register(RangeField)
def convert_posgres_range_to_string(field, registry=None, input_flag=None):
    inner_type = convert_django_field(field.base_field)
    if not isinstance(inner_type, (List, NonNull)):
        inner_type = type(inner_type)
    return List(inner_type, description=field.help_text, required=not field.null and input_flag == 'create')