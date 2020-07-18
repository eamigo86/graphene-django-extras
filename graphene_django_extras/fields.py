# -*- coding: utf-8 -*-
import operator
from functools import partial
from django.db.models import QuerySet
from graphene import Field, List, ID, Argument
from graphene.types.structures import Structure, NonNull
from graphene_django.fields import DjangoListField as DLF
from graphene_django.filter.utils import get_filtering_args_from_filterset
from graphene_django.utils import (
    maybe_queryset,
    is_valid_django_model,
    DJANGO_FILTER_INSTALLED,
)

from graphene_django_extras.filters.filter import get_filterset_class
from graphene_django_extras.node import BaseNodeField
from graphene_django_extras.rest_framework import GraphqlPermissionMixin
from graphene_django_extras.settings import graphql_api_settings
from .base_types import DjangoListObjectBase
from .paginations.pagination import BaseDjangoGraphqlPagination
from .utils import get_extra_filters, queryset_factory, get_related_fields, find_field, _get_queryset, queryset_refactor


# *********************************************** #
# *********** FIELD FOR SINGLE OBJECT *********** #
# *********************************************** #
class DjangoObjectField(Field):
    def __init__(self, _type, *args, **kwargs):
        kwargs["id"] = ID(
            required=True, description="Django object unique identification field"
        )

        super(DjangoObjectField, self).__init__(_type, *args, **kwargs)

    @property
    def model(self):
        return self.type._meta.node._meta.model

    @staticmethod
    def object_resolver(manager, root, info, **kwargs):
        id = kwargs.pop("id", None)

        try:
            return manager.get_queryset().get(pk=id)
        except manager.model.DoesNotExist:
            return None

    def get_resolver(self, parent_resolver):
        return partial(self.object_resolver, self.type._meta.model._default_manager)


# *************************************************************** #
# *********** FIELD FOR SINGLE OBJECT WITH PERMISSION *********** #
# *************************************************************** #
class RetrieveField(BaseNodeField):
    def get_id(self, root, info, **kwargs):
        return kwargs.get('id')


# *********************************************** #
# *************** FIELDS FOR LIST *************** #
# *********************************************** #
class DjangoListField(DLF):
    def __init__(self, _type, *args, **kwargs):
        if isinstance(_type, NonNull):
            _type = _type.of_type

        super(DLF, self).__init__(List(NonNull(_type)), *args, **kwargs)


class DjangoBaseListField(GraphqlPermissionMixin, Field):
    def __init__(
            self,
            _type,
            permission_classes=(),
            output_type=None,
            fields=None,
            extra_filter_meta=None,
            filterset_class=None,
            skip_filters=False,
            *args,
            **kwargs
    ):
        self.filterset_class = {}
        self.filtering_args = {}

        assert isinstance(permission_classes, (tuple, list)), (
            "Permissions can only be a `List` of `Tuple` - ".format(self.__class__.__name__)
        )

        self.permission_classes = permission_classes

        if DJANGO_FILTER_INSTALLED and not skip_filters:
            _fields = _type._meta.filter_fields
            _model = _type._meta.model

            self.fields = fields or _fields
            meta = dict(model=_model, fields=self.fields)
            if extra_filter_meta:
                meta.update(extra_filter_meta)
            filterset_class = filterset_class or _type._meta.filterset_class
            self.filterset_class = get_filterset_class(filterset_class, **meta)
            self.filtering_args = get_filtering_args_from_filterset(
                self.filterset_class, _type
            )
            kwargs.setdefault("args", {})
            kwargs["args"].update(self.filtering_args)

            if "id" not in kwargs["args"].keys():
                kwargs["args"].update(
                    {
                        "id": Argument(
                            ID, description="Django object unique identification field"
                        )
                    }
                )
        if not kwargs.get("description", None):
            kwargs["description"] = "{} list".format(_type._meta.model.__name__)
        self.skip_filters = skip_filters
        super(DjangoBaseListField, self).__init__(output_type or _type, *args, **kwargs)

    @classmethod
    def refactor_query(cls, manager, info, fragments=None, **kwargs):
        return queryset_refactor(manager, info.field_asts, fragments, **kwargs)

    @classmethod
    def get_queryset(cls, manager):
        return _get_queryset(manager)

    @property
    def model(self):
        return self.get_model()

    @classmethod
    def get_model(cls):
        return cls.type._meta.model

    def list_resolver(self, resolver, manager, filterset_class, filtering_args, root, info, **kwargs):
        raise NotImplementedError('list_resolver must be implemented')

    def list_resolver_permission_check(self, resolver, manager, filterset_class,
                                       filtering_args, root, info, **kwargs):
        self.check_permissions(request=info.context)
        return self.list_resolver(resolver, manager, filterset_class, filtering_args, root, info, **kwargs)

    def get_resolver(self, parent_resolver):
        return partial(
            self.list_resolver_permission_check,
            parent_resolver,
            self.type._meta.model._default_manager,
            self.filterset_class,
            self.filtering_args,
        )

    @classmethod
    def _init_pagination_list(cls, pagination):
        pagination_ = pagination
        if pagination_ is None:
            pagination_ = graphql_api_settings.DEFAULT_PAGINATION_CLASS() \
                if graphql_api_settings.DEFAULT_PAGINATION_CLASS else None

        if pagination_ is not None:
            assert isinstance(pagination, BaseDjangoGraphqlPagination), (
                'You need to pass a valid DjangoGraphqlPagination in DjangoFilterPaginateListField, received "{}".'
            ).format(pagination_)

            pagination_kwargs = pagination_.to_graphql_fields()

            return pagination_, pagination_kwargs
        return None


class DjangoBaseFilterListField(DjangoBaseListField):
    def __init__(self, *args, **kwargs):
        super(DjangoBaseFilterListField, self).__init__(*args, **kwargs)

    @classmethod
    def get_model(cls):
        return cls.type.of_type._meta.node._meta.model

    def list_resolver(self, resolver, manager, filterset_class, filtering_args, root, info, **kwargs):
        raise NotImplementedError('list_resolver must be implemented')

    def get_resolver(self, parent_resolver):
        current_type = self.type
        while isinstance(current_type, Structure):
            current_type = current_type.of_type
        return partial(
            self.list_resolver_permission_check,
            parent_resolver,
            current_type._meta.model._default_manager,
            self.filterset_class,
            self.filtering_args,
        )


class FilterListFieldResolverMixin:
    def list_resolver(self, resolver, manager, filterset_class, filtering_args, root, info, **kwargs):
        qs = None
        field = None

        if root and is_valid_django_model(root._meta.model):
            available_related_fields = get_related_fields(root._meta.model)
            field = find_field(info.field_asts[0], available_related_fields)
        filter_kwargs = {k: v for k, v in kwargs.items() if k in filtering_args}

        if field is not None:
            try:
                if filter_kwargs:
                    qs = operator.attrgetter(
                        "{}.filter".format(
                            getattr(field, "related_name", None) or field.name
                        )
                    )(root)(**filter_kwargs)
                else:
                    qs = operator.attrgetter(
                        "{}.all".format(
                            getattr(field, "related_name", None) or field.name
                        )
                    )(root)()
            except AttributeError:
                qs = None

        if qs is None:
            qs = self.get_queryset(manager)
            qs = filterset_class(
                data=filter_kwargs, queryset=qs, request=info.context
            ).qs
            if root and is_valid_django_model(root._meta.model):
                extra_filters = get_extra_filters(root, manager.model)
                qs = qs.filter(**extra_filters)
            qs = self.refactor_query(qs, info, fragments=info.fragments, **kwargs)
        return maybe_queryset(qs)


class DjangoFilterListField(FilterListFieldResolverMixin, DjangoBaseFilterListField):
    def __init__(self, _type, skip_filters=False, *args, **kwargs):
        super(DjangoFilterListField, self).__init__(_type, output_type=List(_type), *args, **kwargs)


class FilterPaginateListFieldResolverMixin:
    def list_resolver(self, resolver, manager, filterset_class, filtering_args, root, info, **kwargs):
        qs_resolve_override = True
        qs = maybe_queryset(resolver(root, info, **kwargs))

        if qs is None:
            qs = self.get_queryset(manager)
            qs_resolve_override = False

        if not self.skip_filters:
            filter_kwargs = {k: v for k, v in kwargs.items() if k in filtering_args}
            qs = filterset_class(data=filter_kwargs, queryset=qs, request=info.context).qs

        if not qs_resolve_override and root and is_valid_django_model(root._meta.model):
            extra_filters = get_extra_filters(root, manager.model)
            qs = qs.filter(**extra_filters)

        if getattr(self, "pagination", None):
            qs = self.pagination.paginate_queryset(qs, **kwargs)

        if not qs_resolve_override:
            qs = self.refactor_query(qs, info, fragments=info.fragments, **kwargs)
        return maybe_queryset(qs)


class DjangoFilterPaginateListField(FilterPaginateListFieldResolverMixin, DjangoBaseFilterListField):
    def __init__(self, _type, pagination=None, *args, **kwargs):

        pagination_ = self._init_pagination_list(pagination=pagination)
        if pagination_:
            pagination, pagination_kwargs = pagination_
            self.pagination = pagination
            kwargs.update(**pagination_kwargs)

        super(DjangoFilterPaginateListField, self).__init__(
            _type, output_type=List(_type), *args, **kwargs
        )


class ListObjectFieldResolverMixin:
    def list_resolver(self, resolver, manager, filterset_class, filtering_args, root, info, **kwargs):
        qs_resolve_override, count = True, 0
        qs = maybe_queryset(resolver(root, info, **kwargs))

        if qs is None:
            qs = self.get_queryset(manager)
            qs_resolve_override = False

        if not self.skip_filters:
            filter_kwargs = {k: v for k, v in kwargs.items() if k in filtering_args}
            qs = filterset_class(data=filter_kwargs, queryset=qs, request=info.context).qs

        count = qs.count()

        if not qs_resolve_override:
            qs = self.refactor_query(qs, info, fragments=info.fragments, **kwargs)

        return DjangoListObjectBase(
            count=count,
            results=maybe_queryset(qs),
            results_field_name=self.type._meta.results_field_name,
        )


class DjangoListObjectField(ListObjectFieldResolverMixin, DjangoBaseListField):
    pass




