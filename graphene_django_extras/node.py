from functools import partial
from graphene import Node, Field, ID
from graphene.types.utils import get_type
from graphene_django.utils import is_valid_django_model
from graphene_django_extras.rest_framework import GraphqlPermissionMixin
from graphene_django_extras.utils import queryset_builder


class BaseNodeField(GraphqlPermissionMixin, Field):

    def __init__(self, _type, permission_classes=(), *args, **kwargs):

        kwargs.setdefault('id', ID(required=True, description='The ID of the object'))
        self.permission_classes = permission_classes

        assert hasattr(_type._meta, "model") and is_valid_django_model(_type._meta.model), (
            'only Django model is allowed'
        )

        self.model = _type._meta.model
        super(BaseNodeField, self).__init__(_type, *args, **kwargs)

    def get_id(self, root, info, **kwargs):
        raise NotImplementedError('Implementation is required')

    def query_resolver(self, root, info, **kwargs):
        self.check_permissions(info.context)
        _id = self.get_id(root, info, **kwargs)

        qs = queryset_builder(self.model, info, filter_kwargs=dict(id=_id))
        obj = qs.first()

        if not obj:
            return obj
        self.check_object_permissions(info.context, obj)
        return obj

    def get_resolver(self, parent_resolver):
        return partial(self.query_resolver)


class DjangoNodeField(BaseNodeField):

    def __init__(self, node, type=False, *args, **kwargs):
        assert issubclass(node, Node), "NodeField can only operate in Nodes"
        self.node_type = node
        self.field_type = type

        super(DjangoNodeField, self).__init__(
            type or node,
            *args,
            **kwargs
        )

    def get_id(self, root, info, **kwargs):
        only_type = get_type(self.field_type)
        return self.node_type.node_resolver(only_type, root, info, **kwargs)


class DjangoNode(Node):
    @classmethod
    def Field(cls, *args, **kwargs):
        return DjangoNodeField(cls, *args, **kwargs)

    @classmethod
    def get_node_from_global_id(cls, info, global_id, only_type=None):
        try:
            _type, _id = Node.from_global_id(global_id)
            graphene_type = info.schema.get_type(_type).graphene_type
        except Exception as e:
            return None

        if only_type:
            assert graphene_type == only_type, ("Must receive a {} id.").format(
                only_type._meta.name
            )

        # We make sure the ObjectType implements the "Node" interface
        if cls.__base__ not in graphene_type._meta.interfaces:
            return None

        return _id
