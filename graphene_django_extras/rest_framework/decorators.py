from functools import wraps
from graphql import GraphQLError

from apps.core.object_mixins import GraphqlPermissionMixin


def login_required(f, not_auth_msg=None):
    @wraps(f)
    def wrap(*args, **kwargs):
        _, info = args
        if info.context.user.is_authenticated:
            return f(*args, **kwargs)
        raise GraphQLError(not_auth_msg or 'Authentication is required')
    return wrap


def permission_required(f, permissions=None):
    wrap_permission_mixin = GraphqlPermissionMixin()
    wrap_permission_mixin.permission_classes = permissions or []
    @wraps(f)
    def wrap(*args, **kwargs):
        _, info = args
        wrap_permission_mixin.check_permissions(info.context)
        return f(*args, **kwargs)
    return wrap


def is_super_user_required(f, no_auth_msg=None, not_auth_msg=None):
    @wraps(f)
    def wrap(*args, **kwargs):
        _, info = args
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError(no_auth_msg or 'Authentication is required')
        if not user.is_superuser:
            raise GraphQLError(not_auth_msg or 'Not Authorized')
        return f(*args, **kwargs)

    return wrap


def is_staff_required(f, no_auth_msg=None, not_auth_msg=None):
    @wraps(f)
    def wrap(*args, **kwargs):
        _, info = args
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError(no_auth_msg or'Authentication is required')
        if not user.is_superuser or not user.is_staff:
            raise GraphQLError(not_auth_msg or 'Not Authorised')
        return f(*args, **kwargs)
    return wrap
