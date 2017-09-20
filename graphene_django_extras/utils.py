# -*- coding: utf-8 -*-
from django.db.models import QuerySet, Manager
from django.db.models.base import ModelBase
from graphene.utils.str_converters import to_snake_case


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
        raise ValueError("Object is of type '{}', but must be a Django Model, "
                         "Manager, or QuerySet".format(klass__name))
    return manager.all()


def get_Object_or_None(klass, *args, **kwargs):
    """
    Uses get() to return an object, or None if the object does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.
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


def kwargs_formatter(**kwargs):
    if kwargs.get('deprecation_reason', None):
        kwargs['deprecation_reason'] = 'DEPRECATED: {}'.format(kwargs['deprecation_reason'])

    return kwargs


def get_extra_filters(root, model):
    extra_filters = {}
    for field in model._meta.get_fields():
        if field.is_relation and field.related_model == root._meta.model:
            extra_filters.update({field.name: root})

    return extra_filters


def get_related_fields(model):
    return {field.name: field for field in model._meta.get_fields() if field.is_relation}


def find_field(field, fields_dict):
    temp = fields_dict.get(
        field.name.value,
        fields_dict.get(
            to_snake_case(field.name.value),
            None)
    )

    return temp


def recursive_params(selection_set, available_related_fields, select_related, prefetch_related):

    for field in selection_set.selections:

        temp = available_related_fields.get(
            field.name.value,
            available_related_fields.get(
                to_snake_case(field.name.value),
                None)
        )

        if temp:
            if (temp.many_to_many or temp.one_to_many) and temp.name not in prefetch_related:
                prefetch_related.append(temp.name)
            elif temp.name not in select_related:
                select_related.append(temp.name)
        elif field.selection_set:
            a, b = recursive_params(field.selection_set, available_related_fields, select_related, prefetch_related)
            [select_related.append(x) for x in a if x not in select_related]
            [prefetch_related.append(x) for x in b if x not in prefetch_related]

    return select_related, prefetch_related


def queryset_factory(manager, fields_asts=None, filtering_args=None, **kwargs):

    if filtering_args is None:
        filtering_args = {}
    select_related = []
    prefetch_related = []
    filter_kwargs = {k: v for k, v in kwargs.items() if k in filtering_args}
    available_related_fields = get_related_fields(manager.model)

    for f in kwargs.keys():
        temp = available_related_fields.get(f.split('_', 1)[0], None)
        if temp:
            if (temp.many_to_many or temp.one_to_many) and temp.name not in prefetch_related:
                prefetch_related.append(temp.name)
            else:
                select_related.append(temp.name)

    if fields_asts:
        select_related, prefetch_related = recursive_params(fields_asts[0].selection_set, available_related_fields, select_related, prefetch_related)

    if select_related and prefetch_related:
        return manager.filter(**filter_kwargs).select_related(*select_related).prefetch_related(*prefetch_related)
    elif not select_related and prefetch_related:
        return manager.filter(**filter_kwargs).prefetch_related(*prefetch_related)
    elif select_related and not prefetch_related:
        return manager.filter(**filter_kwargs).select_related(*select_related)
    return manager.filter(**filter_kwargs)
