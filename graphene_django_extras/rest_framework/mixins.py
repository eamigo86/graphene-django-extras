from graphene_django.types import ErrorType
from graphql import GraphQLError
from rest_framework.exceptions import ValidationError
from graphene_django_extras.utils import get_Object_or_None

__all__ = (
    'GraphqlPermissionMixin', 'CreateSerializerMixin', 'UpdateModelMixin',
    'CreateModelMixin', 'DeleteModelMixin', 'UpdateSerializerMixin',
)


class GraphqlPermissionMixin(object):
    """
    DRF based permissions implementation
    """
    permission_classes = []

    @staticmethod
    def permission_denied(permission):
        message = getattr(permission, 'message', None)
        raise GraphQLError(message)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        return [permission() for permission in self.permission_classes]

    def check_permissions(self, request):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in self.get_permissions():
            if not permission.has_permission(request, self):
                self.permission_denied(permission)

    def check_object_permissions(self, request, obj):
        """
        Check if the request should be permitted for a given object.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in self.get_permissions():
            if not permission.has_object_permission(request, self, obj):
                self.permission_denied(permission)


class CreateSerializerMixin(object):
    """
    CreateMutation Implementation
    """

    def perform_create(self, root, info, data, **kwargs):
        serializer = self._meta.serializer_class(data=data)
        obj = self.save(serialized_obj=serializer, root=root, info=info)
        return obj

    @classmethod
    def create(cls, root, info, **kwargs):
        self = cls()
        self.check_permissions(request=info.context)
        data = {}
        if cls._meta.input_field_name:
            data = kwargs.get(cls._meta.input_field_name)
        else:
            data.update(**kwargs)
        request_type = info.context.META.get("CONTENT_TYPE", "")
        if "multipart/form-data" in request_type:
            data.update({name: value for name, value in info.context.FILES.items()})
        try:
            obj = self.perform_create(root, info, data, **kwargs)
            assert obj is not None, (
                '`perform_create()` did not return an object instance.'
            )
            return self.perform_mutate(obj, info)
        except Exception as e:
            if isinstance(e, ValidationError):
                errors = self.error_builder(e.detail.serializer)
                return self.get_errors(errors)


class UpdateSerializerMixin(object):
    """
        UpdateMutation Implementation
    """

    def get_object(self, info, data, **kwargs):
        look_up_field = self.get_lookup_field_name()
        look_up_value = data.get(look_up_field)
        filter_kwargs = {look_up_field: look_up_value}
        return get_Object_or_None(self._get_model(), **filter_kwargs)

    def perform_update(self, root, info, data, instance, **kwargs):
        serializer = self._meta.serializer_class(
            instance,
            data=data,
            partial=True,
        )
        obj = self.save(serializer, root=root, info=info)
        return obj

    @classmethod
    def update(cls, root, info, **kwargs):
        self = cls()
        self.check_permissions(request=info.context)

        data = {}
        if cls._meta.input_field_name:
            data = kwargs.get(cls._meta.input_field_name)
        else:
            data.update(**kwargs)

        request_type = info.context.META.get("CONTENT_TYPE", "")
        if "multipart/form-data" in request_type:
            data.update({name: value for name, value in info.context.FILES.items()})

        existing_obj = self.get_object(info, data, **kwargs)
        if existing_obj:
            self.check_object_permissions(request=info.context, obj=existing_obj)
            try:
                obj = self.perform_update(root=root, info=info, data=data, instance=existing_obj, **kwargs)
                assert obj is not None, (
                    '`perform_update()` did not return an object instance.'
                )
                return self.perform_mutate(obj, info)
            except Exception as e:
                if isinstance(e, ValidationError):
                    errors = self.error_builder(e.detail.serializer)
                    return self.get_errors(errors)
        else:
            pk = data.get(cls._get_lookup_field_name())
            return cls.get_errors(
                [
                    ErrorType(
                        field="id",
                        messages=[
                            "A {} obj with id: {} do not exist".format(
                                self._get_model().__name__, pk
                            )
                        ],
                    )
                ]
            )


class DeleteModelMixin(object):
    """
    DeleteMutation Implementation
    """
    
    def perform_delete(self, info, obj, **kwargs):
        obj.delete()

    def get_object(self, info, data, **kwargs):
        look_up_field = self.get_lookup_field_name()
        look_up_value = data.get(look_up_field)
        filter_kwargs = {look_up_field: look_up_value}
        return get_Object_or_None(self._get_model(), **filter_kwargs)

    @classmethod
    def delete(cls, root, info, **kwargs):
        self = cls()
        self.check_permissions(request=info.context)

        pk = kwargs.get(self._get_lookup_field_name())

        old_obj = self.get_object(info, data=kwargs)

        if old_obj:
            self.check_object_permissions(request=info.context, obj=old_obj)
            self.perform_delete(info=info, obj=old_obj, **kwargs)
            if not old_obj.id:
                old_obj.id = pk
            return self.perform_mutate(old_obj, info)
        else:
            return self.get_errors(
                [
                    ErrorType(
                        field="id",
                        messages=[
                            "A {} obj with id {} do not exist".format(
                                self._get_model().__name__, pk
                            )
                        ],
                    )
                ]
            )


class CreateModelMixin(CreateSerializerMixin):
    def create_mutate(self, info, data, **kwargs):
        """Creates the model and returns the created object"""
        raise NotImplementedError('`create_mutate` method needs to be implemented'.format(self.__class__.__name__))

    def perform_create(self, root, info, data, **kwargs):
        try:
            obj = self.create_mutate(info, data, **kwargs)
            assert obj is not None, (
                '`create_mutate()` did not return an object instance.'
            )
            return self.perform_mutate(obj, info)
        except Exception as e:
            if isinstance(e, ValidationError):
                errors = self.error_builder(e.detail.serializer)
                return self.get_errors(errors)
            
            messages = [str(e)]
            return self.get_errors([ErrorType(
                messages=messages,
            )])


class UpdateModelMixin(UpdateSerializerMixin):
    def update_mutate(self, info, data, instance, **kwargs):
        """Updates a model and returns the updated object"""
        raise NotImplementedError('`update_mutate` method needs to be implemented'.format(self.__class__.__name__))

    def perform_update(self, root, info, data, instance, **kwargs):
        """
        Updates a model and returns the updated object
        """
        try:
            self.update_mutate(info, data, instance,  **kwargs)
            return self.perform_mutate(obj=instance, info=info, data=data, **kwargs)
        except Exception as e:
            if isinstance(e, ValidationError):
                errors = self.error_builder(e.detail.serializer)
                return self.get_errors(errors)
            
            messages = [str(e)]
            return self.get_errors([ErrorType(
                messages=messages,
            )])


