# Quick Start

This guide will help you get started with graphene-django-extras quickly.

## Configuration

Configure global settings for pagination in your Django settings:

```python title="settings.py"
GRAPHENE_DJANGO_EXTRAS = {
    'DEFAULT_PAGINATION_CLASS': 'graphene_django_extras.paginations.LimitOffsetGraphqlPagination',
    'DEFAULT_PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 50,
    'CACHE_ACTIVE': True,
    'CACHE_TIMEOUT': 300    # seconds
}
```

## Types Definition

### Basic Type

```python title="types.py"
from django.contrib.auth.models import User
from graphene_django_extras import DjangoObjectType

class UserType(DjangoObjectType):
    class Meta:
        model = User
        description = "Type definition for a single user"
        filter_fields = {
            "id": ("exact", ),
            "first_name": ("icontains", "iexact"),
            "last_name": ("icontains", "iexact"),
            "username": ("icontains", "iexact"),
            "email": ("icontains", "iexact"),
            "is_staff": ("exact", ),
        }
```

### List Type with Pagination

```python title="types.py"
from graphene_django_extras import DjangoListObjectType
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

class UserListType(DjangoListObjectType):
    class Meta:
        description = "Type definition for user list"
        model = User
        pagination = LimitOffsetGraphqlPagination(
            default_limit=25,
            ordering="-username"  # Can be string, tuple, or list
        )
```

### Serializer Type

```python title="types.py"
from graphene_django_extras import DjangoSerializerType
from .serializers import UserSerializer

class UserModelType(DjangoSerializerType):
    """With this type definition, mutations are auto-generated"""

    class Meta:
        description = "User model type definition"
        serializer_class = UserSerializer
        pagination = LimitOffsetGraphqlPagination(
            default_limit=25,
            ordering="-username"
        )
        filter_fields = {
            "id": ("exact", ),
            "first_name": ("icontains", "iexact"),
            "last_name": ("icontains", "iexact"),
            "username": ("icontains", "iexact"),
            "email": ("icontains", "iexact"),
            "is_staff": ("exact", ),
        }
```

## Input Types

Define input types for mutations:

```python title="inputs.py"
from graphene_django_extras import DjangoInputObjectType
from django.contrib.auth.models import User

class UserInput(DjangoInputObjectType):
    class Meta:
        description = "User InputType definition for mutations"
        model = User
```

## Mutations

### Serializer-based Mutations

!!! tip "Recommended Approach"
    DjangoSerializerMutation automatically implements Create, Delete and Update functions.

```python title="mutations.py"
from graphene_django_extras import DjangoSerializerMutation
from .serializers import UserSerializer

class UserSerializerMutation(DjangoSerializerMutation):
    class Meta:
        description = "DRF serializer based Mutation for Users"
        serializer_class = UserSerializer
```

### Traditional Mutations

```python title="mutations.py"
import graphene
from .types import UserType
from .inputs import UserInput

class UserMutation(graphene.Mutation):
    """Traditional mutation - requires implementing mutate function"""

    user = graphene.Field(UserType, required=False)

    class Arguments:
        new_user = graphene.Argument(UserInput)

    class Meta:
        description = "Graphene traditional mutation for Users"

    @classmethod
    def mutate(cls, root, info, *args, **kwargs):
        # Implement your mutation logic here
        pass
```

## Schema Definition

```python title="schema.py"
import graphene
from graphene_django_extras import (
    DjangoObjectField,
    DjangoListObjectField,
    DjangoFilterPaginateListField,
    DjangoFilterListField,
    LimitOffsetGraphqlPagination
)
from .types import UserType, UserListType, UserModelType
from .mutations import UserMutation, UserSerializerMutation

class Query(graphene.ObjectType):
    # Different ways to define user list queries
    users = DjangoListObjectField(UserListType, description='All Users query')
    users_paginated = DjangoFilterPaginateListField(
        UserType,
        pagination=LimitOffsetGraphqlPagination()
    )
    users_filtered = DjangoFilterListField(UserType)

    # Single user queries
    user = DjangoObjectField(UserType, description='Single User query')
    user_detail = UserListType.RetrieveField(description='User detail')

    # Using DjangoSerializerType
    user_retrieve, user_list = UserModelType.QueryFields(
        description='User queries with serializer type'
    )

class Mutation(graphene.ObjectType):
    # Serializer-based mutations
    user_create = UserSerializerMutation.CreateField()
    user_delete = UserSerializerMutation.DeleteField()
    user_update = UserSerializerMutation.UpdateField()

    # Using DjangoSerializerType
    user_create_alt, user_delete_alt, user_update_alt = UserModelType.MutationFields()

    # Traditional mutation
    traditional_user_mutation = UserMutation.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
```

## Example Queries

=== "List Query"

    ```graphql
    {
      users(limit: 5, offset: 0) {
        results {
          id
          username
          firstName
          lastName
        }
        totalCount
      }
    }
    ```

=== "Filtered Query"

    ```graphql
    {
      users(firstName_Icontains: "john", limit: 10) {
        results {
          id
          username
          firstName
          lastName
        }
        totalCount
      }
    }
    ```

=== "Single User"

    ```graphql
    {
      user(id: 1) {
        id
        username
        firstName
        lastName
        email
      }
    }
    ```

## Example Mutations

=== "Create User"

    ```graphql
    mutation {
      userCreate(newUser: {username: "test", password: "test123"}) {
        user {
          id
          username
          firstName
          lastName
        }
        ok
        errors {
          field
          messages
        }
      }
    }
    ```

=== "Update User"

    ```graphql
    mutation {
      userUpdate(newUser: {id: 1, username: "newusername"}) {
        user {
          id
          username
        }
        ok
        errors {
          field
          messages
        }
      }
    }
    ```

=== "Delete User"

    ```graphql
    mutation {
      userDelete(id: 1) {
        ok
        errors {
          field
          messages
        }
      }
    }
    ```

## Next Steps

- Learn more about [Fields](usage/fields.md)
- Explore [Pagination](usage/pagination.md) options
- Discover [Directives](directives.md) for data formatting
- Check out more [Examples](usage/examples.md)
