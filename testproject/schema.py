from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
import graphene
from graphene_django_extras import DjangoListObjectType, DjangoSerializerType, DjangoObjectType
from graphene_django_extras import DjangoObjectField, DjangoListObjectField, DjangoFilterPaginateListField, DjangoFilterListField
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

import serializers
import filtersets


class UserType(DjangoObjectType):
    class Meta:
        model = User
        description = " Type definition for a single user "
        filter_fields = {
            'id': ['exact', ],
            'first_name': ['icontains', 'iexact'],
            'last_name': ['icontains', 'iexact'],
            'username': ['icontains', 'iexact'],
            'email': ['icontains', 'iexact']
        }


class UserListType(DjangoListObjectType):
    class Meta:
        description = " Type definition for user list "
        model = User
        pagination = LimitOffsetGraphqlPagination(default_limit=25, ordering="-username")


# class UserModelType(DjangoSerializerType):
#     """ With this type definition it't necessary a mutation definition for user's model """
# 
#     class Meta:
#         description = " User's model type definition "
#         serializer_class = serializers.UserSerializer
#         pagination = LimitOffsetGraphqlPagination(default_limit=25, ordering="-username")
#         filter_fields = {
#             'id': ['exact', ],
#             'first_name': ['icontains', 'iexact'],
#             'last_name': ['icontains', 'iexact'],
#             'username': ['icontains', 'iexact'],
#             'email': ['icontains', 'iexact'],
#             'is_staff': ['exact']
#         }


class Query(graphene.ObjectType):
    # Possible User list queries definitions
    all_users = DjangoListObjectField(UserListType, description=_('All Users query'))
    all_users1 = DjangoFilterPaginateListField(UserType, pagination=LimitOffsetGraphqlPagination())
    all_users2 = DjangoFilterListField(UserType)
    all_users3 = DjangoListObjectField(UserListType, filterset_class=filtersets.UserFilter, description=_('All Users query'))

    # Defining a query for a single user
    # The DjangoObjectField have a ID type input field, that allow filter by id and is't necessary to define resolve function
    user = DjangoObjectField(UserType, description=_('Single User query'))

    # Another way to define a query to single user
    user1 = UserListType.RetrieveField(description=_('User List with pagination and filtering'))

    # Exist two ways to define single or list user queries with DjangoSerializerType
    # user_retrieve1, user_list1 = UserModelType.QueryFields(description='Some description message for both queries',
    #                                                        deprecation_reason='Some deprecation message for both queries')
    # user_retrieve2 = UserModelType.RetrieveField(description='Some description message for retrieve query',
    #                                              deprecation_reason='Some deprecation message for retrieve query')
    # user_list2 = UserModelType.ListField(description='Some description message for list query',
    #                                      deprecation_reason='Some deprecation message for list query')

schema = graphene.Schema(query=Query)
