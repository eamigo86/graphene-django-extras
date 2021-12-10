import datetime

import graphene
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from graphene_django_extras import all_directives
from graphene_django_extras.base_types import CustomDateTime, CustomDate, CustomTime
from graphene_django_extras.fields import (
    DjangoObjectField,
    DjangoListObjectField,
    DjangoFilterPaginateListField,
    DjangoFilterListField,
)
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination, PageGraphqlPagination
from graphene_django_extras.types import (
    DjangoListObjectType,
    DjangoSerializerType,
    DjangoObjectType,
)
from .filtersets import UserFilterSet
from .serializers import UserSerializer


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

class User2ListType(DjangoListObjectType):
    class Meta:
        description = " Type definition for user list "
        model = User
        pagination = PageGraphqlPagination(
            page_size_query_param="page_size",
            page_size=10
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
    all_users1_1 = DjangoListObjectField(
        User2ListType
    )
    all_users2 = DjangoFilterListField(UserType)
    all_users3 = DjangoListObjectField(
        User1ListType, filterset_class=UserFilterSet, description=_("All Users query")
    )
    all_users4 = DjangoFilterListField(UserType)

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

    datetime_ = CustomDateTime(name="datetime")
    date_ = CustomDate(name="date")
    time_ = CustomTime(name="time")

    def resolve_datetime_(self, info, *args, **kwargs):
        return datetime.datetime(2020, 12, 31, 10, 21, 30)

    def resolve_date_(self, info, *args, **kwargs):
        return datetime.date(2020, 12, 31)

    def resolve_time_(self, info, *args, **kwargs):
        return datetime.time(10, 21, 30)

    @staticmethod
    def resolve_all_users4(root, info, **kwargs):
        return User.objects.filter(is_staff=True)


schema = graphene.Schema(query=Query, directives=all_directives)
