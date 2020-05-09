from collections import Iterable
from functools import partial
from django.db.models import QuerySet
from graphene import NonNull
from graphene.relay.connection import IterableConnectionField, PageInfo
from graphene.utils.thenables import maybe_thenable
from graphene_django import DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay.connection.arrayconnection import connection_from_list_slice
from graphene_django_extras.settings import graphql_api_settings


class ConnectionField(IterableConnectionField):

    @classmethod
    def resolve_connection(cls, connection_type, args, resolved):
        if isinstance(resolved, connection_type):
            return resolved

        assert isinstance(resolved, Iterable), (
            "Resolved value from the connection field have to be iterable or instance of {}. "
            'Received "{}"'
        ).format(connection_type, resolved)

        if isinstance(resolved, QuerySet):
            _len = resolved.count()
        else:
            _len = len(resolved)
        connection = connection_from_list_slice(
            resolved,
            args,
            slice_start=0,
            list_length=_len,
            list_slice_length=_len,
            connection_type=connection_type,
            edge_type=connection_type.Edge,
            pageinfo_type=PageInfo,
        )
        connection.iterable = resolved
        return connection

    @classmethod
    def connection_resolver(cls, resolver, connection_type, root, info, **args):
        resolved = resolver(root, info, **args)

        first = args.get('first')
        last = args.get('last')

        if not first and not last:
            args['first'] = graphql_api_settings.DEFAULT_PAGE_SIZE

        if isinstance(connection_type, NonNull):
            connection_type = connection_type.of_type

        if not resolved and getattr(connection_type, 'resolve_objects', None):
            resolved = connection_type.resolve_objects(root, info, **args)

        on_resolve = partial(cls.resolve_connection, connection_type, args)
        return maybe_thenable(resolved, on_resolve)


class DjangoConnectionPageLimitField(DjangoConnectionField):

    @classmethod
    def connection_resolver(cls, *args, **kwargs):
        first = kwargs.get('first')
        last = kwargs.get('last')

        if not first and not last:
            kwargs['first'] = graphql_api_settings.DEFAULT_PAGE_SIZE
        return DjangoConnectionField.connection_resolver(*args, **kwargs)


class DjangoFieldConnectionPageLimitField(DjangoFilterConnectionField, DjangoConnectionPageLimitField):
    pass
