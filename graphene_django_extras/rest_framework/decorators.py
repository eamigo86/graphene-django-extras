from functools import wraps

from django.db.models import QuerySet
from graphene_django.utils import maybe_queryset
from graphql import GraphQLError

from .mixins import GraphqlPermissionMixin

__all__ = [
    "permission_required",
    "is_super_user_required_msg",
    "is_staff_required_msg",
    "login_required_msg",
    "is_super_user_required",
    "is_staff_required",
    "login_required",
]


def login_required_msg(no_auth_msg):
    """
    :param no_auth_msg: No Authentication message
    """
    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            root, info = args
            if info.context.user.is_authenticated:
                return f(*args, **kwargs)
            raise GraphQLError(no_auth_msg)

        return wrap

    return decorator


def permission_required(permission_classes):
    """
    :param permission_classes: list of permission_classes
    """
    assert isinstance(permission_classes, (list, tuple)), 'permission_classes must be instance of `list` or `tuple` '
    wrap_permission_mixin = GraphqlPermissionMixin()
    wrap_permission_mixin.permission_classes = permission_classes

    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            root, info = args
            wrap_permission_mixin.check_permissions(info.context)
            result = f(*args, **kwargs)
            qs = maybe_queryset(result)
            if isinstance(qs, QuerySet) and qs.exists():
                wrap_permission_mixin.check_object_permissions(info.context, qs.first())
            elif isinstance(qs, (list, tuple)) and len(qs) > 0:
                wrap_permission_mixin.check_object_permissions(info.context, qs[0])
            return result
        return wrap
    return decorator


def is_super_user_required_msg(no_auth_msg, not_auth_msg=None):
    """
    :param no_auth_msg: No Authentication message
    :param not_auth_msg: Not Authorized message
    """

    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            root, info = args
            user = info.context.user
            if not user.is_authenticated:
                raise GraphQLError(no_auth_msg)
            if not user.is_superuser:
                raise GraphQLError(not_auth_msg or 'Not Authorized')
            return f(*args, **kwargs)

        return wrap

    return decorator


def is_staff_required_msg(no_auth_msg, not_auth_msg=None):
    """
    :param no_auth_msg: No Authentication message
    :param not_auth_msg: Not Authorized message
    """

    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            root, info = args
            user = info.context.user
            if not user.is_authenticated:
                raise GraphQLError(no_auth_msg)
            if not user.is_superuser or not user.is_staff:
                raise GraphQLError(not_auth_msg or 'Not Authorised')
            return f(*args, **kwargs)

        return wrap

    return decorator


login_required = login_required_msg('Authentication is required')
is_super_user_required = is_super_user_required_msg('Authentication is required')
is_staff_required = is_staff_required_msg('Authentication is required')
