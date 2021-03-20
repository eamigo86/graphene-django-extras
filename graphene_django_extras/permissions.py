from .exceptions import PermissionDenied

def check_authenticated(user):
    return user and user.is_authenticated


def assert_authenticated(user, msg=None):
    if not check_authenticated(user):
        raise PermissionDenied(msg or "You don't have permissions to do this...")


def check_superuser(user):
    return check_authenticated(user) and user.is_superuser


def assert_superuser(user, msg=None):
    if not check_superuser(user):
        raise PermissionDenied(msg or "You don't have permissions to do this...")


def check_perms(user, perms, any_perm=True, with_superuser=True):
    if not check_authenticated(user):
        return False

    if with_superuser and check_superuser(user):
        return True

    u_perms = set(user.get_all_permissions())
    f = any if any_perm else all
    return f(p in u_perms for p in perms)