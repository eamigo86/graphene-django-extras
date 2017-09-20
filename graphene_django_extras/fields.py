# -*- coding: utf-8 -*-
import operator
from functools import partial

from django.utils.translation import ugettext_lazy as _
from graphene import Field, List, ID, Argument
from graphene_django.filter.utils import get_filtering_args_from_filterset
from graphene_django.utils import maybe_queryset, is_valid_django_model, DJANGO_FILTER_INSTALLED

from .base_types import DjangoListObjectBase
from .filter import get_filterset_class
from .pagination.utils import list_pagination_factory
from .utils import get_extra_filters, kwargs_formatter, queryset_factory, get_related_fields, find_field


# *********************************************** #
# *********** FIELD FOR SINGLE OBJECT *********** #
# *********************************************** #
class DjangoObjectField(Field):
    def __init__(self, _type, preprocess_kwargs=None, *args, **kwargs):

        kwargs.setdefault('args', {})
        kwargs['id'] = ID(required=True, description=_('Django object unique identification field'))

        preprocess_kwargs = preprocess_kwargs or kwargs_formatter
        kwargs = preprocess_kwargs(**kwargs)

        super(DjangoObjectField, self).__init__(_type, *args, **kwargs)

    @property
    def model(self):
        return self.type._meta.node._meta.model

    @staticmethod
    def object_resolver(manager, root, info, **kwargs):
        id = kwargs.pop('id', None)

        try:
            return manager.get_queryset().get(pk=id)
        except manager.model.DoesNotExist:
            return None

    def get_resolver(self, parent_resolver):
        return partial(self.object_resolver, self.type._meta.model._default_manager)


# *********************************************** #
# *************** FIELDS FOR LIST *************** #
# *********************************************** #
class DjangoListField(Field):

    def __init__(self, _type, preprocess_kwargs=None, *args, **kwargs):

        preprocess_kwargs = preprocess_kwargs or kwargs_formatter
        kwargs = preprocess_kwargs(**kwargs)

        super(DjangoListField, self).__init__(List(_type), *args, **kwargs)

    @property
    def model(self):
        return self.type.of_type._meta.node._meta.model

    @staticmethod
    def list_resolver(resolver, root, info, **args):
        return maybe_queryset(resolver(root, info, **args))

    def get_resolver(self, parent_resolver):
        return partial(self.list_resolver, parent_resolver)


class DjangoFilterListField(Field):

    def __init__(self, _type, fields=None, extra_filter_meta=None,
                 filterset_class=None, preprocess_kwargs=None, *args, **kwargs):

        if DJANGO_FILTER_INSTALLED:
            _fields = _type._meta.filter_fields
            _model = _type._meta.model

            self.fields = fields or _fields
            meta = dict(model=_model, fields=self.fields)
            if extra_filter_meta:
                meta.update(extra_filter_meta)
            self.filterset_class = get_filterset_class(filterset_class, **meta)
            self.filtering_args = get_filtering_args_from_filterset(self.filterset_class, _type)
            kwargs.setdefault('args', {})
            kwargs['args'].update(self.filtering_args)

            if 'id' not in kwargs['args'].keys():
                self.filtering_args.update({'id': Argument(ID,
                                                           description=_('Django object unique identification field'))})
                kwargs['args'].update({'id': Argument(ID, description=_('Django object unique identification field'))})

        if not kwargs.get('description', None):
            kwargs['description'] = _('List of {} objects').format(_type._meta.model.__name__)

        preprocess_kwargs = preprocess_kwargs or kwargs_formatter
        kwargs = preprocess_kwargs(**kwargs)

        super(DjangoFilterListField, self).__init__(List(_type), *args, **kwargs)

    @property
    def model(self):
        return self.type.of_type._meta.node._meta.model

    @staticmethod
    def list_resolver1(manager, filterset_class, filtering_args,
                       root, info, **kwargs):
        qs = find_field(info.field_asts[0], root._prefetched_objects_cache)

        if not qs:
            qs = queryset_factory(manager, info.field_asts, filtering_args, **kwargs)

            if root and is_valid_django_model(root._meta.model):
                extra_filters = get_extra_filters(root, manager.model)
                qs = qs.filter(**extra_filters)

        return qs

    @staticmethod
    def list_resolver(manager, filterset_class, filtering_args,
                      root, info, **kwargs):
        qs = None
        available_related_fields = get_related_fields(root._meta.model)
        field = find_field(info.field_asts[0], available_related_fields)

        if field:
            try:
                filter_kwargs = {k: v for k, v in kwargs.items() if k in filtering_args}
                if filter_kwargs:
                    qs = operator.attrgetter(
                        '{}.filter'.format(
                            getattr(field, 'related_name', None) or field.name))(root)(**filter_kwargs)
                else:
                    qs = operator.attrgetter(
                        '{}.all'.format(
                            getattr(field, 'related_name', None) or field.name))(root)()
            except AttributeError:
                qs = None

        if qs is None:
            qs = queryset_factory(manager, info.field_asts, filtering_args, **kwargs)

            if root and is_valid_django_model(root._meta.model):
                extra_filters = get_extra_filters(root, manager.model)
                qs = qs.filter(**extra_filters)

        return qs

    def get_resolver(self, parent_resolver):
        return partial(self.list_resolver, self.type.of_type._meta.model._default_manager,
                       self.filterset_class, self.filtering_args)


class DjangoFilterPaginateListField(Field):
    def __init__(self, _type, pagination=None, fields=None, extra_filter_meta=None,
                 filterset_class=None, preprocess_kwargs=None, *args, **kwargs):

        _fields = _type._meta.filter_fields
        _model = _type._meta.model

        self.fields = fields or _fields
        meta = dict(model=_model, fields=self.fields)
        if extra_filter_meta:
            meta.update(extra_filter_meta)
        self.filterset_class = get_filterset_class(filterset_class, **meta)
        self.filtering_args = get_filtering_args_from_filterset(self.filterset_class, _type)
        kwargs.setdefault('args', {})
        kwargs['args'].update(self.filtering_args)

        if 'id' not in kwargs['args'].keys():
            self.filtering_args.update({'id': Argument(ID, description=_('Django object unique identification field'))})
            kwargs['args'].update({'id': Argument(ID, description=_('Django object unique identification field'))})

        if pagination:
            pagination_kwargs = list_pagination_factory(pagination)

            self.pagination = pagination
            kwargs.update(**pagination_kwargs)

        if not kwargs.get('description', None):
            kwargs['description'] = _('List of {} objects').format(_type._meta.model.__name__)

        preprocess_kwargs = preprocess_kwargs or kwargs_formatter
        kwargs = preprocess_kwargs(**kwargs)

        super(DjangoFilterPaginateListField, self).__init__(List(_type), *args, **kwargs)

    @property
    def model(self):
        return self.type.of_type._meta.node._meta.model

    def list_resolver(self, manager, filterset_class, filtering_args,
                      root, info, **kwargs):

        filter_kwargs = {k: v for k, v in kwargs.items() if k in filtering_args}
        # qs = manager.get_queryset()
        # qs = filterset_class(data=filter_kwargs, queryset=qs).qs
        qs = manager.get_queryset().filter(**filter_kwargs)

        if getattr(self, 'pagination', None):
            qs = self.pagination.paginate_queryset(qs, **kwargs)

        return maybe_queryset(qs)

    def get_resolver(self, parent_resolver):
        return partial(self.list_resolver, self.type.of_type._meta.model._default_manager,
                       self.filterset_class, self.filtering_args)


class DjangoListObjectField(Field):

    def __init__(self, _type, fields=None, extra_filter_meta=None,
                 filterset_class=None, preprocess_kwargs=None, *args, **kwargs):

        if DJANGO_FILTER_INSTALLED:
            _fields = _type._meta.filter_fields
            _model = _type._meta.model

            self.fields = fields or _fields

            meta = dict(model=_model, fields=self.fields)
            if extra_filter_meta:
                meta.update(extra_filter_meta)

            self.filterset_class = get_filterset_class(filterset_class, **meta)
            self.filtering_args = get_filtering_args_from_filterset(self.filterset_class, _type)
            kwargs.setdefault('args', {})
            kwargs['args'].update(self.filtering_args)

            if 'id' not in kwargs['args'].keys():
                self.filtering_args.update({'id': Argument(ID,
                                                           description=_('Django object unique identification field'))})
                kwargs['args'].update({'id': Argument(ID, description=_('Django object unique identification field'))})

        if not kwargs.get('description', None):
            kwargs['description'] = _('List of {} objects').format(_type._meta.model.__name__)

        preprocess_kwargs = preprocess_kwargs or kwargs_formatter
        kwargs = preprocess_kwargs(**kwargs)

        super(DjangoListObjectField, self).__init__(_type, *args, **kwargs)

    @property
    def model(self):
        return self.type._meta.model

    def list_resolver(self, manager, filterset_class, filtering_args, root, info, **kwargs):

        qs = queryset_factory(manager, info.field_asts, filtering_args, **kwargs)
        # filter_kwargs = {k: v for k, v in kwargs.items() if k in filtering_args}

        # qs = manager.get_queryset()
        # qs = filterset_class(data=filter_kwargs, queryset=qs).qs
        # qs = manager.get_queryset().filter(**filter_kwargs)
        count = qs.count()

        return DjangoListObjectBase(
            count=count,
            results=qs,
            results_field_name=self.type._meta.results_field_name
        )

    def get_resolver(self, parent_resolver):
        return partial(self.list_resolver, self.type._meta.model._default_manager,
                       self.filterset_class, self.filtering_args)
