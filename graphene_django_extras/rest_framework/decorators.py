from functools import wraps
from graphql import GraphQLError

from .mixins import GraphqlPermissionMixin

__all__ = [
    "login_required",
    "permission_required",
    "is_super_user_required",
    "is_staff_required",
]


def login_required(not_auth_msg=None):
    """
    :param not_auth_msg: not authorization message
    :return: f
    """
    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            root, info = args
            if info.context.user.is_authenticated:
                return f(*args, **kwargs)
            raise GraphQLError(not_auth_msg or 'Authentication is required')
        return wrap
    return decorator


def permission_required(permissions=None):
    """
    :param permissions: list of permission_classes
    :return:
    """
    wrap_permission_mixin = GraphqlPermissionMixin()
    wrap_permission_mixin.permission_classes = permissions or []

    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            root, info = args
            wrap_permission_mixin.check_permissions(info.context)
            return f(wrap_permission_mixin, root=root, info=info, **kwargs)
        return wrap
    return decorator


def is_super_user_required(no_auth_msg=None, not_auth_msg=None):
    """
    :param no_auth_msg: No authentication message
    :param not_auth_msg: Not authorized message
    :return: f
    """

    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            root, info = args
            user = info.context.user
            if not user.is_authenticated:
                raise GraphQLError(no_auth_msg or 'Authentication is required')
            if not user.is_superuser:
                raise GraphQLError(not_auth_msg or 'Not Authorized')
            return f(*args, **kwargs)

        return wrap
    return decorator


def is_staff_required(no_auth_msg=None, not_auth_msg=None):
    """
    :param no_auth_msg: No authentication message
    :param not_auth_msg: Not authorized message
    :return: f
    """

    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            root, info = args
            user = info.context.user
            if not user.is_authenticated:
                raise GraphQLError(no_auth_msg or'Authentication is required')
            if not user.is_superuser or not user.is_staff:
                raise GraphQLError(not_auth_msg or 'Not Authorised')
            return f(*args, **kwargs)
        return wrap
    return decorator
