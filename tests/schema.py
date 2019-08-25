import graphene
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from graphene_django_extras.types import (
    DjangoListObjectType,
    DjangoSerializerType,
    DjangoObjectType,
)
from graphene_django_extras.fields import (
    DjangoObjectField,
    DjangoListObjectField,
    DjangoFilterPaginateListField,
    DjangoFilterListField,
)
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

from .serializers import UserSerializer
from .filtersets import UserFilterSet


class UserType(DjangoObjectType):
    class Meta:
        model = User
        description = " Type definition for a single user "
        filter_fields = {
            "id": ("exact",),
            "first_name": ("icontains", "iexact"),
            "last_name": ("icontains", "iexact"),
            "username": ("icontains", "iexact"),
            "email": ("icontains", "iexact"),
        }


class User1ListType(DjangoListObjectType):
    class Meta:
        description = " Type definition for user list "
        model = User
        pagination = LimitOffsetGraphqlPagination(
            default_limit=25, ordering="-username"
        )


class UserModelType(DjangoSerializerType):
    class Meta:
        description = " Serializer Type definition for user "
        serializer_class = UserSerializer
        pagination = LimitOffsetGraphqlPagination(
            default_limit=25, ordering="-username"
        )
        filterset_class = UserFilterSet


# class UserModelType(DjangoSerializerType):
#     """ With this type definition it't necessary a mutation definition for user's model """
#
#     class Meta:
#         description = " User's model type definition "
#         serializer_class = serializers.UserSerializer
#         pagination = LimitOffsetGraphqlPagination(default_limit=25, ordering="-username")
#         filter_fields = {
#             'id': ('exact', ),
#             'first_name': ('icontains', 'iexact'),
#             'last_name': ('icontains', 'iexact'),
#             'username': ('icontains', 'iexact'),
#             'email': ('icontains', 'iexact'),
#             'is_staff': ('exact',)
#         }


class Query(graphene.ObjectType):
    # Possible User list queries definitions
    all_users = DjangoListObjectField(User1ListType, description=_("All Users query"))
    all_users1 = DjangoFilterPaginateListField(
        UserType, pagination=LimitOffsetGraphqlPagination()
    )
    all_users2 = DjangoFilterListField(UserType)
    all_users3 = DjangoListObjectField(
        User1ListType, filterset_class=UserFilterSet, description=_("All Users query")
    )

    # Defining a query for a single user
    # The DjangoObjectField have a ID type input field,
    # that allow filter by id and is't necessary to define resolve function
    user = DjangoObjectField(UserType, description=_("Single User query"))

    # Another way to define a query to single user
    user1 = User1ListType.RetrieveField(
        description=_("User List with pagination and filtering")
    )

    # Exist two ways to define single or list user queries with DjangoSerializerType
    user2, users = UserModelType.QueryFields()


schema = graphene.Schema(query=Query)
