import graphene
from django.contrib.auth.models import User
from graphene_django import DjangoObjectType

from .models import BasicModel
from .serializers import UserSerializer, BasicSerializer
from rest_framework.permissions import IsAuthenticated

from graphene_django_extras.rest_framework import (
    DRFSerializerMutation,
    DjangoModelMutation
)

__all__ = ('Mutation', 'BasicModelType', 'BasicModelNodeType')


class BasicModelType(DjangoObjectType):
    class Meta:
        model = BasicModel


class BasicModelNodeType(DjangoObjectType):
    class Meta:
        model = BasicModel
        interfaces = (graphene.relay.Node,)


class BasicSerializerMutation(DRFSerializerMutation):
    serializer_class_as_output = True
    mutation_serializers = {  # optional if you want to be specific
        'create': BasicSerializer,
        'update': BasicSerializer
    }

    class Meta:
        serializer_class = BasicSerializer  # compulsory global serializer


class BasicModelMutation(DjangoModelMutation):
    # create_fields = dict(
    #     only_fields=('text',),
    #     # exclude_fields=('',)
    # )
    #
    # update_fields = dict(
    #     only_fields=('text',),
    #     # exclude_fields=('',)
    # )

    permission_classes = (IsAuthenticated,)

    def create_mutate(self, info, data, **kwargs) -> object:
        serialized_obj = BasicSerializer(data=data)
        serialized_obj.is_valid(raise_exception=True)
        return serialized_obj.save()

    def update_mutate(self, info, data, instance, **kwargs) -> object:
        serialized_obj = BasicSerializer(data=data, instance=instance, partial=True)
        serialized_obj.is_valid(raise_exception=True)
        return serialized_obj.save()

    class Meta:
        model = BasicModel
        only_fields = ('text', )


class Mutation(graphene.ObjectType):
    create_basic_se = BasicSerializerMutation.CreateField(
        description='Create basic model using serializer inputs'
    )
    update_basic_se = BasicSerializerMutation.UpdateField(
        description='Update basic model using serializer'
    )
    delete_basic_se = BasicSerializerMutation.DeleteField(
        description='Delete basic model using serializer'
    )

    create_basic = BasicModelMutation.CreateField(
        description='Create basic model for only permitted users'
    )
    update_basic = BasicModelMutation.UpdateField(
        description='Update basic model for only permitted users'
    )
    delete_basic = BasicModelMutation.DeleteField(
        description='Delete basic model for only permitted users'
    )
