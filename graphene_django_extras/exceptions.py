from django.core.exceptions import PermissionDenied as _PermissionDenied

class PermissionDenied(_PermissionDenied):

    default_message = "You do not have permission to perform this action"

    def __init__(self, message=None):
        if message is None:
            message = self.default_message

        super().__init__(message)