from django.core.exceptions import ValidationError as Django_ValidationError
from graphene_django.types import ErrorType
from graphql import GraphQLError
from rest_framework.exceptions import ValidationError as Serializer_ValidationError
from graphene_django_extras.utils import get_Object_or_None, merge_related_queries
from graphene_django_extras.utils import _get_queryset
from graphql_relay import from_global_id

__all__ = (
    'GraphqlPermissionMixin', 'CreateSerializerMixin', 'UpdateModelMixin',
    'CreateModelMixin', 'DeleteModelMixin', 'UpdateSerializerMixin', 'GetObjectQueryMixin',
    'NodeGetObjectQueryMixin'
)


class ObjectBaseMixin(object):
    @classmethod
    def error_builder(cls, serialized_obj):
        errors = [
            ErrorType(field=key, messages=value)
            for key, value in serialized_obj.errors.items()
        ]
        return errors

    @classmethod
    def django_error_builder(cls, error_list):
        errors = [
            ErrorType(messages=item.messages)
            for item in error_list
        ]
        return errors

    @classmethod
    def construct_error(cls, message, field=None,):
        return list(ErrorType(field=field, messages=list(message)))

    def _handle_errors(self, e):
        if isinstance(e, Serializer_ValidationError):
            errors = self.error_builder(e.detail.serializer)
            return self.get_errors(errors)
        if isinstance(e, Django_ValidationError):
            errors = self.django_error_builder(e.error_list)
            return self.get_errors(errors)

        messages = e.__str__()
        return self.get_errors(
            [
                ErrorType(
                    field="id",
                    messages=[messages],
                )
            ]
        )

    def get_object(self, info, data, **kwargs):
        look_up_field = self.get_lookup_field_name()
        lookup_url_kwarg = self.lookup_url_kwarg or look_up_field
        lookup_url_kwarg_value = data.get(lookup_url_kwarg) or kwargs.get(lookup_url_kwarg)
        filter_kwargs = {look_up_field: lookup_url_kwarg_value}
        return get_Object_or_None(self._get_model(), **filter_kwargs)


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


class CreateSerializerMixin(ObjectBaseMixin):
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
            return self._handle_errors(e)


class UpdateSerializerMixin(ObjectBaseMixin):
    """
        UpdateMutation Implementation
    """

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

        try:
            existing_obj = self.get_object(info, data, **kwargs)
            if existing_obj:
                self.check_object_permissions(request=info.context, obj=existing_obj)
                obj = self.perform_update(root=root, info=info, data=data, instance=existing_obj, **kwargs)
                assert obj is not None, (
                    '`perform_update()` did not return an object instance.'
                )
                return self.perform_mutate(obj, info)

            else:
                pk = data.get(cls._get_lookup_field_name())
                errors = cls.construct_error(
                    field="id", message="A {} obj with id: {} do not exist".format(self._get_model().__name__, pk)
                )
                return cls.get_errors(errors)
        except Exception as e:
            return self._handle_errors(e)


class DeleteModelMixin(ObjectBaseMixin):
    """
    DeleteMutation Implementation
    """
    
    def perform_delete(self, info, obj, **kwargs):
        obj.delete()

    @classmethod
    def delete(cls, root, info, **kwargs):
        self = cls()
        self.check_permissions(request=info.context)

        pk = kwargs.get(self.get_lookup_field_name())
        try:
            old_obj = self.get_object(info, data=kwargs)

            if old_obj:
                self.check_object_permissions(request=info.context, obj=old_obj)
                self.perform_delete(info=info, obj=old_obj, **kwargs)
                if not old_obj.id:
                    old_obj.id = pk
                return self.perform_mutate(old_obj, info)
            else:
                errors = cls.construct_error(
                    field="id", message="A {} obj with id: {} do not exist".format(self._get_model().__name__, pk)
                )
                return cls.get_errors(errors)
        except Exception as e:
            return self._handle_errors(e)


class CreateModelMixin(CreateSerializerMixin):
    def create_mutate(self, info, data, **kwargs):
        """Creates the model and returns the created object"""
        raise NotImplementedError('`create_mutate` method needs to be implemented'.format(self.__class__.__name__))

    def perform_create(self, root, info, data, **kwargs):
        obj = self.create_mutate(info, data, **kwargs)
        assert obj is not None, (
            '`create_mutate()` did not return an object instance.'
        )
        return obj


class UpdateModelMixin(UpdateSerializerMixin):
    def update_mutate(self, info, data, instance, **kwargs):
        """Updates a model and returns the updated object"""
        raise NotImplementedError('`update_mutate` method needs to be implemented'.format(self.__class__.__name__))

    def perform_update(self, root, info, data, instance, **kwargs):
        """
        Updates a model and returns the updated object
        """
        update_obj = self.update_mutate(info, data, instance, **kwargs)
        assert update_obj is not None, (
            '`update_mutate()` did not return an object instance.'
        )
        return update_obj


class GetObjectQueryMixin:
    select_related = []
    prefetch_related = []
    filter_kwargs = dict()

    def get_filter_kwargs(self):
        if self.filter_kwargs:
            assert isinstance(self.filter_kwargs, dict), (
                '`filter_kwargs` must be a dict'
            )
        return self.filter_kwargs

    def build_query(self, filter_kwargs):
        klass = self._get_model()
        queryset = _get_queryset(klass)

        if self.select_related is not None:
            assert isinstance(self.select_related, (list, tuple)), (
                '`select_related` must be a list or tuple'
            )

        if self.prefetch_related is not None:
            assert isinstance(self.prefetch_related, (list, tuple)), (
                '`prefetch_related` must be a list or tuple'
            )

        queryset = queryset.filter(**filter_kwargs)

        obj_query = merge_related_queries(
            queryset, select_related=self.select_related,
            prefetch_related=self.prefetch_related
        )

        return obj_query

    def get_object(self, info, data, **kwargs):
        """
        Gets object for a model type
        :param info: graphene info object
        :param data: data input
        :param kwargs: other inputs
        :return: object of model from `self.get_model()`
        """
        look_up_field = self.get_lookup_field_name()

        lookup_url_kwarg = self.lookup_url_kwarg or look_up_field
        lookup_url_kwarg_value = data.get(lookup_url_kwarg) or kwargs.get(lookup_url_kwarg)

        filter_kwargs = self.get_filter_kwargs()
        filter_kwargs.update({look_up_field: lookup_url_kwarg_value})

        obj_query = self.build_query(filter_kwargs)

        return obj_query.first()


class NodeGetObjectQueryMixin(GetObjectQueryMixin):

    @classmethod
    def get_model_id(cls, node_id):
        _type, _id = from_global_id(node_id)
        return _id

    def get_object(self, info, data, **kwargs):
        """
        Gets object for a node model type
        :param info: graphene info object
        :param data: data input
        :param kwargs: other inputs
        :return: object of model from `self.get_model()`
        """
        look_up_field = self.get_lookup_field_name()

        lookup_url_kwarg = self.lookup_url_kwarg or look_up_field
        lookup_url_kwarg_value = data.get(lookup_url_kwarg) or kwargs.get(lookup_url_kwarg)
        look_up_value = self.get_model_id(lookup_url_kwarg_value)

        filter_kwargs = self.get_filter_kwargs()
        filter_kwargs.update({look_up_field: look_up_value})

        obj_query = self.build_query(filter_kwargs)

        return obj_query.first()


