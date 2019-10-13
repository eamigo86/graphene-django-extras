# -*- coding: utf-8 -*-
import operator
from functools import partial

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
from graphene_django_extras.settings import graphql_api_settings
from .base_types import DjangoListObjectBase
from .paginations.pagination import BaseDjangoGraphqlPagination
from .utils import get_extra_filters, queryset_factory, get_related_fields, find_field


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


# *********************************************** #
# *************** FIELDS FOR LIST *************** #
# *********************************************** #
class DjangoListField(DLF):
    def __init__(self, _type, *args, **kwargs):
        if isinstance(_type, NonNull):
            _type = _type.of_type

        super(DLF, self).__init__(List(NonNull(_type)), *args, **kwargs)


class DjangoFilterListField(Field):
    def __init__(
        self,
        _type,
        fields=None,
        extra_filter_meta=None,
        filterset_class=None,
        *args,
        **kwargs,
    ):

        if DJANGO_FILTER_INSTALLED:
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
                self.filtering_args.update(
                    {
                        "id": Argument(
                            ID, description="Django object unique identification field"
                        )
                    }
                )
                kwargs["args"].update(
                    {
                        "id": Argument(
                            ID, description="Django object unique identification field"
                        )
                    }
                )

        if not kwargs.get("description", None):
            kwargs["description"] = "{} list".format(_type._meta.model.__name__)

        super(DjangoFilterListField, self).__init__(List(_type), *args, **kwargs)

    @property
    def model(self):
        return self.type.of_type._meta.node._meta.model

    @staticmethod
    def list_resolver(manager, filterset_class, filtering_args, root, info, **kwargs):
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
            qs = queryset_factory(manager, info.field_asts, info.fragments, **kwargs)
            qs = filterset_class(
                data=filter_kwargs, queryset=qs, request=info.context
            ).qs

            if root and is_valid_django_model(root._meta.model):
                extra_filters = get_extra_filters(root, manager.model)
                qs = qs.filter(**extra_filters)

        return maybe_queryset(qs)

    def get_resolver(self, parent_resolver):
        current_type = self.type
        while isinstance(current_type, Structure):
            current_type = current_type.of_type
        return partial(
            self.list_resolver,
            current_type._meta.model._default_manager,
            self.filterset_class,
            self.filtering_args,
        )


class DjangoFilterPaginateListField(Field):
    def __init__(
        self,
        _type,
        pagination=None,
        fields=None,
        extra_filter_meta=None,
        filterset_class=None,
        *args,
        **kwargs,
    ):

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
            self.filtering_args.update(
                {
                    "id": Argument(
                        ID, description="Django object unique identification field"
                    )
                }
            )
            kwargs["args"].update(
                {
                    "id": Argument(
                        ID, description="Django object unique identification field"
                    )
                }
            )

        pagination = pagination or graphql_api_settings.DEFAULT_PAGINATION_CLASS()

        if pagination is not None:
            assert isinstance(pagination, BaseDjangoGraphqlPagination), (
                'You need to pass a valid DjangoGraphqlPagination in DjangoFilterPaginateListField, received "{}".'
            ).format(pagination)

            pagination_kwargs = pagination.to_graphql_fields()

            self.pagination = pagination
            kwargs.update(**pagination_kwargs)

        if not kwargs.get("description", None):
            kwargs["description"] = "{} list".format(_type._meta.model.__name__)

        super(DjangoFilterPaginateListField, self).__init__(
            List(_type), *args, **kwargs
        )

    @property
    def model(self):
        return self.type.of_type._meta.node._meta.model

    def get_queryset(self, manager, info, **kwargs):
        return queryset_factory(manager, info.field_asts, info.fragments, **kwargs)

    def list_resolver(
        self, manager, filterset_class, filtering_args, root, info, **kwargs
    ):
        filter_kwargs = {k: v for k, v in kwargs.items() if k in filtering_args}
        qs = self.get_queryset(manager, info, **kwargs)
        qs = filterset_class(data=filter_kwargs, queryset=qs, request=info.context).qs

        if root and is_valid_django_model(root._meta.model):
            extra_filters = get_extra_filters(root, manager.model)
            qs = qs.filter(**extra_filters)

        if getattr(self, "pagination", None):
            qs = self.pagination.paginate_queryset(qs, **kwargs)

        return maybe_queryset(qs)

    def get_resolver(self, parent_resolver):
        current_type = self.type
        while isinstance(current_type, Structure):
            current_type = current_type.of_type
        return partial(
            self.list_resolver,
            current_type._meta.model._default_manager,
            self.filterset_class,
            self.filtering_args,
        )


class DjangoListObjectField(Field):
    def __init__(
        self,
        _type,
        fields=None,
        extra_filter_meta=None,
        filterset_class=None,
        *args,
        **kwargs,
    ):

        if DJANGO_FILTER_INSTALLED:
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
                id_description = "Django object unique identification field"
                self.filtering_args.update(
                    {"id": Argument(ID, description=id_description)}
                )
                kwargs["args"].update({"id": Argument(ID, description=id_description)})

        if not kwargs.get("description", None):
            kwargs["description"] = "{} list".format(_type._meta.model.__name__)

        super(DjangoListObjectField, self).__init__(_type, *args, **kwargs)

    @property
    def model(self):
        return self.type._meta.model

    def list_resolver(
        self, manager, filterset_class, filtering_args, root, info, **kwargs
    ):

        qs = queryset_factory(manager, info.field_asts, info.fragments, **kwargs)

        filter_kwargs = {k: v for k, v in kwargs.items() if k in filtering_args}

        qs = filterset_class(data=filter_kwargs, queryset=qs, request=info.context).qs
        count = qs.count()

        return DjangoListObjectBase(
            count=count,
            results=maybe_queryset(qs),
            results_field_name=self.type._meta.results_field_name,
        )

    def get_resolver(self, parent_resolver):
        return partial(
            self.list_resolver,
            self.type._meta.model._default_manager,
            self.filterset_class,
            self.filtering_args,
        )
