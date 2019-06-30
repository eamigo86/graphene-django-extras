# -*- coding: utf-8 -*-
import inspect
import re
from collections import OrderedDict

import six
from django import VERSION as DJANGO_VERSION
from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRel
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.db.models import (
    NOT_PROVIDED,
    QuerySet,
    Manager,
    Model,
    ManyToOneRel,
    ManyToManyRel,
)
from django.db.models.base import ModelBase
from graphene.utils.str_converters import to_snake_case
from graphene_django.utils import is_valid_django_model
from graphql import GraphQLList, GraphQLNonNull
from graphql.language.ast import FragmentSpread, InlineFragment


def get_reverse_fields(model):
    reverse_fields = {
        f.name: f for f in model._meta.get_fields() if f.auto_created and not f.concrete
    }

    for name, field in reverse_fields.items():
        # Django =>1.9 uses 'rel', django <1.9 uses 'related'
        related = getattr(field, "rel", None) or getattr(field, "related", None)
        if isinstance(related, ManyToOneRel):
            yield (name, related)
        elif isinstance(related, ManyToManyRel) and not related.symmetrical:
            yield (name, related)


def _resolve_model(obj):
    """
    Resolve supplied `obj` to a Django model class.

    `obj` must be a Django model class itself, or a string
    representation of one.  Useful in situations like GH #1225 where
    Django may not have resolved a string-based reference to a model in
    another model's foreign key definition.

    String representations should have the format:
        'appname.ModelName'
    """
    if isinstance(obj, six.string_types) and len(obj.split(".")) == 2:
        app_name, model_name = obj.split(".")
        resolved_model = apps.get_model(app_name, model_name)
        if resolved_model is None:
            msg = "Django did not return a model for {0}.{1}"
            raise ImproperlyConfigured(msg.format(app_name, model_name))
        return resolved_model
    elif inspect.isclass(obj) and issubclass(obj, Model):
        return obj
    raise ValueError("{0} is not a Django model".format(obj))


def to_kebab_case(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", name.title().replace(" ", ""))
    return re.sub("([a-z0-9])([A-Z])", r"\1-\2", s1).lower()


def get_related_model(field):
    # Backward compatibility patch for Django versions lower than 1.9.x
    if DJANGO_VERSION < (1, 9):
        return _resolve_model(field.rel.to)
    return field.remote_field.model


def get_model_fields(model):
    # Backward compatibility patch for Django versions lower than 1.11.x
    if DJANGO_VERSION >= (1, 11):
        private_fields = model._meta.private_fields
    else:
        private_fields = model._meta.virtual_fields

    all_fields_list = (
        list(model._meta.fields)
        + list(model._meta.local_many_to_many)
        + list(private_fields)
        + list(model._meta.fields_map.values())
    )

    # Make sure we don't duplicate local fields with "reverse" version
    # and get the real reverse django related_name
    reverse_fields = list(get_reverse_fields(model))
    exclude_fields = [field[1] for field in reverse_fields]

    local_fields = [
        (field.name, field) for field in all_fields_list if field not in exclude_fields
    ]

    all_fields = local_fields + reverse_fields

    return all_fields


def get_obj(app_label, model_name, object_id):
    """
    Function used to get a object
    :param app_label: A valid Django Model or a string with format: <app_label>.<model_name>
    :param model_name: Key into kwargs that contains de data: new_person
    :param object_id:
    :return: instance
    """
    try:
        model = apps.get_model("{}.{}".format(app_label, model_name))
        assert is_valid_django_model(model), ("Model {}.{} do not exist.").format(
            app_label, model_name
        )

        obj = get_Object_or_None(model, pk=object_id)
        return obj

    except model.DoesNotExist:
        return None
    except LookupError:
        pass
    except ValidationError as e:
        raise ValidationError(e.__str__())
    except TypeError as e:
        raise TypeError(e.__str__())
    except Exception as e:
        raise Exception(e.__str__())


def create_obj(django_model, new_obj_key=None, *args, **kwargs):
    """
    Function used by my on traditional Mutations to create objs
    :param django_model: A valid Django Model or a string with format:
    <app_label>.<model_name>
    :param new_obj_key: Key into kwargs that contains de data: new_person
    :param args:
    :param kwargs: Dict with model attributes values
    :return: instance of model after saved it
    """

    try:
        if isinstance(django_model, six.string_types):
            django_model = apps.get_model(django_model)
        assert is_valid_django_model(django_model), (
            "You need to pass a valid Django Model or a string with format: "
            '<app_label>.<model_name> to "create_obj"'
            ' function, received "{}".'
        ).format(django_model)

        data = kwargs.get(new_obj_key, None) if new_obj_key else kwargs
        new_obj = django_model(**data)
        new_obj.full_clean()
        new_obj.save()
        return new_obj
    except LookupError:
        pass
    except ValidationError as e:
        raise ValidationError(e.__str__())
    except TypeError as e:
        raise TypeError(e.__str__())
    except Exception as e:
        return e.__str__()


def clean_dict(d):
    """
        Remove all empty fields in a nested dict
    """

    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (clean_dict(v) for v in d) if v]
    return OrderedDict(
        [(k, v) for k, v in ((k, clean_dict(v)) for k, v in list(d.items())) if v]
    )


def get_type(_type):
    if isinstance(_type, (GraphQLList, GraphQLNonNull)):
        return get_type(_type.of_type)
    return _type


def get_fields(info):
    fragments = info.fragments
    field_asts = info.field_asts[0].selection_set.selections

    for field_ast in field_asts:
        field_name = field_ast.name.value
        if isinstance(field_ast, FragmentSpread):
            for field in fragments[field_name].selection_set.selections:
                yield field.name.value
            continue

        yield field_name


def is_required(field):
    try:
        blank = getattr(field, "blank", getattr(field, "field", None))
        default = getattr(field, "default", getattr(field, "field", None))
        #  null = getattr(field, "null", getattr(field, "field", None))

        if blank is None:
            blank = True
        elif not isinstance(blank, bool):
            blank = getattr(blank, "blank", True)

        if default is None:
            default = NOT_PROVIDED
        elif default != NOT_PROVIDED:
            default = getattr(default, "default", default)

    except AttributeError:
        return False

    return not blank and default == NOT_PROVIDED


def _get_queryset(klass):
    """
    Returns a QuerySet from a Model, Manager, or QuerySet. Created to make
    get_object_or_404 and get_list_or_404 more DRY.

    Raises a ValueError if klass is not a Model, Manager, or QuerySet.
    """
    if isinstance(klass, QuerySet):
        return klass
    elif isinstance(klass, Manager):
        manager = klass
    elif isinstance(klass, ModelBase):
        manager = klass._default_manager
    else:
        if isinstance(klass, type):
            klass__name = klass.__name__
        else:
            klass__name = klass.__class__.__name__
        raise ValueError(
            "Object is of type '{}', but must be a Django Model, "
            "Manager, or QuerySet".format(klass__name)
        )
    return manager.all()


def get_Object_or_None(klass, *args, **kwargs):
    """
    Uses get() to return an object, or None if the object does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised
    if more than one object is found.
    Ex: get_Object_or_None(User, db, id=1)
    """
    queryset = _get_queryset(klass)
    try:
        if args:
            return queryset.using(args[0]).get(**kwargs)
        else:
            return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None
    # except queryset.model.MultipleObjectsReturned:
    # return get_Objects_or_None(klass, *args, **kwargs)


def get_extra_filters(root, model):
    extra_filters = {}
    for field in model._meta.get_fields():
        if field.is_relation and field.related_model == root._meta.model:
            extra_filters.update({field.name: root})

    return extra_filters


def get_related_fields(model):
    return {
        field.name: field
        for field in model._meta.get_fields()
        if field.is_relation and not isinstance(field, (GenericForeignKey, GenericRel))
    }


def find_field(field, fields_dict):
    temp = fields_dict.get(
        field.name.value, fields_dict.get(to_snake_case(field.name.value), None)
    )

    return temp


def recursive_params(
    selection_set, fragments, available_related_fields, select_related, prefetch_related
):

    for field in selection_set.selections:

        if isinstance(field, FragmentSpread) and fragments:
            a, b = recursive_params(
                fragments[field.name.value].selection_set,
                fragments,
                available_related_fields,
                select_related,
                prefetch_related,
            )
            [select_related.append(x) for x in a if x not in select_related]
            [prefetch_related.append(x) for x in b if x not in prefetch_related]
            continue

        if isinstance(field, InlineFragment):
            a, b = recursive_params(
                field.selection_set,
                fragments,
                available_related_fields,
                select_related,
                prefetch_related,
            )
            [select_related.append(x) for x in a if x not in select_related]
            [prefetch_related.append(x) for x in b if x not in prefetch_related]
            continue

        temp = available_related_fields.get(
            field.name.value,
            available_related_fields.get(to_snake_case(field.name.value), None),
        )

        if temp and temp.name not in [prefetch_related + select_related]:
            if temp.many_to_many or temp.one_to_many:
                prefetch_related.append(temp.name)
            else:
                select_related.append(temp.name)
        elif getattr(field, "selection_set", None):
            a, b = recursive_params(
                field.selection_set,
                fragments,
                available_related_fields,
                select_related,
                prefetch_related,
            )
            [select_related.append(x) for x in a if x not in select_related]
            [prefetch_related.append(x) for x in b if x not in prefetch_related]

    return select_related, prefetch_related


def queryset_factory(manager, fields_asts=None, fragments=None, **kwargs):

    select_related = []
    prefetch_related = []
    available_related_fields = get_related_fields(manager.model)

    for f in kwargs.keys():
        temp = available_related_fields.get(f.split("__", 1)[0], None)
        if temp:
            if (
                temp.many_to_many or temp.one_to_many
            ) and temp.name not in prefetch_related:
                prefetch_related.append(temp.name)
            else:
                select_related.append(temp.name)

    if fields_asts:
        select_related, prefetch_related = recursive_params(
            fields_asts[0].selection_set,
            fragments,
            available_related_fields,
            select_related,
            prefetch_related,
        )

    if select_related and prefetch_related:
        return _get_queryset(
            manager.select_related(*select_related).prefetch_related(*prefetch_related)
        )
    elif not select_related and prefetch_related:
        return _get_queryset(manager.prefetch_related(*prefetch_related))
    elif select_related and not prefetch_related:
        return _get_queryset(manager.select_related(*select_related))
    return _get_queryset(manager)


def parse_validation_exc(validation_exc):

    errors_list = []
    for key, value in validation_exc.error_dict.items():
        for exc in value:
            errors_list.append({"field": key, "messages": exc.messages})

    return errors_list
