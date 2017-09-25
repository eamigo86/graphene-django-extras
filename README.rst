

Graphene-Django-Extras
======================

This package add some extra functionalities to graphene-django to facilitate the graphql use without Relay and
allow pagination and filtering integration.

Installation:
-------------

For installing graphene-django-extras, just run this command in your shell:

.. code:: bash

    pip install "graphene-django-extras"

Documentation:
--------------
Extra functionalities:
    Fields:
      1. DjangoFilterListField
      2. DjangoFilterPaginateListField
      3. DjangoListObjectField (Recommended)

    Mutations:
        1.	DjangoSerializerMutation

    Types:
        1.  DjangoObjectTypeExtra
        2.	DjangoListObjectType
        3.	DjangoInputObjectType

    Pagination:
        1.	LimitOffsetGraphqlPagination
        2.	PageGraphqlPagination
        3.	CursorGraphqlPagination (coming soon)

Examples:
---------

Here is a simple use of graphene-django-extras:

1- Types Definition:

.. code:: python

    from django.contrib.auth.models import User
    from graphene_django_extras import DjangoObjectType, DjangoListObjectType    
    from graphene_django_extras.pagination import LimitOffsetGraphqlPagination

    class UserType(DjangoObjectType):
        """
            This DjangoObjectType have a ID field, that allow filter by id and resolve method definition on Queries is not necessary
        """

        class Meta:
            model = User
            description = " Type definition for single User model object "
            filter_fields = {
                'id': ['exact', ],
                'first_name': ['icontains', 'iexact'],
                'last_name': ['icontains', 'iexact'],
                'username': ['icontains', 'iexact'],
                'email': ['icontains', 'iexact']
            }

    class UserListType(DjangoListObjectType):
        class Meta:
            description = " Type definition for List of users "
            model = User
            pagination = LimitOffsetGraphqlPagination()


2- Input Types can be defined for use on mutations:

.. code:: python

    from graphene_django_extras import DjangoInputObjectType

    class UserInput(DjangoInputObjectType):
        class Meta:
            description = " User Input Type for used as input on Arguments classes on traditional Mutations "
            model = User


3- You can define traditional mutations that use Input Types or Mutations based on DRF SerializerClass:

.. code:: python        

    import graphene
    from .serializers import UserSerializer
    from graphene_django_extras import DjangoSerializerMutation
    from .types import UserType
    from .input_types import UserInputType

    class UserSerializerMutation(DjangoSerializerMutation):
        """
            DjangoSerializerMutation auto implement Create, Delete and Update function
        """
        class Meta:
            description = " Serializer based Mutation for Users "
            serializer_class = UserSerializer


    class UserMutation(graphene.mutation):
        """
            To traditional graphene's mutation classes definition you must implement the mutate function
        """

        user = graphene.Field(UserType, required=False)

        class Arguments:
            new_user = graphene.Argument(UserInput)

        class Meta:
            description = " Traditional graphene mutation for Users "

        @classmethod
        def mutate(cls, info, **kwargs):
            ...


4- Defining schemes:

.. code:: python  

    import graphene
    from graphene_django_extras import DjangoObjectField, DjangoListObjectField
    from .types import UserType, UserListType
    from .mutations import UserMutation, UserSerializerMutation

    class Queries(graphene.ObjectType):
        # Possible User list queries definitions
        all_users = DjangoListObjectField(UserListType, description=_('All Users query'))
        all_users1 = DjangoFilterPaginateListField(UserType, pagination=LimitOffsetGraphqlPagination())
        all_users2 = DjangoFilterListField(UserType)
        all_users3 = DjangoListObjectField(UserListType, filterset_class=UserFilter, description=_('All Users query'))

        # Defining the petition to a user
        user = DjangoObjectField(UserType, description=_('Only one user'))  

        # Another way to define a single user query
        other_way_user = DjangoObjectField(UserListType.getOne(), description=_('User List with pagination and filtering'))  

    class Mutations(graphene.ObjectType):
        user_create = UserSerializerMutation.CreateField(deprecation_reason='Deprecation message')
        user_delete = UserSerializerMutation.DeleteField()
        user_update = UserSerializerMutation.UpdateField()

        traditional_user_mutation = UserMutation.Field()


5- Examples of queries:

.. code:: python

    {
        allUsers(username_Icontains:"john"){
            results(limit:5, offset:5){
                id
                username
                firstName
                lastName
            }
            totalCount
        }

        allUsers1(lastName_Iexact:"Doe", limit:5, offset:0){
            id
            username
            firstName
            lastName    
        }

        allUsers2(firstName_Icontains: "J"){
            id
            username
            firstName
            lastName
        }

        user(id:2){
            id
            username
            firstName
        }
    }


6- Examples of Mutations:

.. code:: python

    mutation{
        userCreate(newUser:{password:"test*123", email: "test@test.com", username:"test"}){
            user{
                id
                username
                firstName
                lastName
            }
            ok
            errors{
                field
                messages
            }
        }

        userDelete(id:1){
            ok
            errors{
                field
                messages
            }
        }

        userUpdate(newUser:{id:1, username:"John"}){
            user{
                id
                username
            }
            ok
            errors{
                field
                messages
            }
        }
    }
