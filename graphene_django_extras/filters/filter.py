# -*- coding: utf-8 -*-
from django_filters.filterset import BaseFilterSet, FilterSet
from django_filters.filterset import FILTER_FOR_DBFIELD_DEFAULTS
from graphene_django.filter.utils import replace_csv_filters


def get_filterset_class(filterset_class, **meta):
    """
    Get the class to be used as the FilterSet.
    """
    if filterset_class:
        # If were given a FilterSet class, then set it up.
        graphene_filterset_class = setup_filterset(filterset_class)
    else:
        # Otherwise create one.
        graphene_filterset_class = custom_filterset_factory(**meta)

    replace_csv_filters(graphene_filterset_class)

    return graphene_filterset_class


class GrapheneFilterSetMixin(BaseFilterSet):
    FILTER_DEFAULTS = FILTER_FOR_DBFIELD_DEFAULTS


def setup_filterset(filterset_class):
    """Wrap a provided filterset in Graphene-specific functionality"""
    return type(
        "Graphene{}".format(filterset_class.__name__),
        (filterset_class, GrapheneFilterSetMixin),
        {},
    )


def custom_filterset_factory(model, filterset_base_class=FilterSet, **meta):
    """
    Create a filterset for the given model using the provided meta data
    """
    meta.update({"model": model, "exclude": []})
    meta_class = type(str("Meta"), (object,), meta)
    filterset = type(
        str("%sFilterSet" % model._meta.object_name),
        (filterset_base_class, GrapheneFilterSetMixin),
        {"Meta": meta_class},
    )
    return filterset
