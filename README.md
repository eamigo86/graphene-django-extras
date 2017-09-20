
---

# ![Graphene Logo](http://graphene-python.org/favicon.png) Graphene-Django-Extras [![PyPI version](https://badge.fury.io/py/graphene-django-extras.svg)](https://badge.fury.io/py/graphene-django-extras) 


This package add some extra funcionalities to graphene-django to facilitate the graphql use without Relay and 
allow pagination and filtering integration.

## Installation

For installing graphene-django-extras, just run this command in your shell

```bash
pip install graphene-django-extras
```

## Documentation

### Extra functionalities:
    Fields:
        1.	DjangoListField
        2.	DjangoFilterListField
        3.	DjangoFilterPaginateListField
        4.	DjangoListObjectField

    Mutations:
        1.	DjangoSerializerMutation

    Types:
        1.  DjangoObjectTypeExtra
        2.	DjangoInputObjectType
        3.	DjangoPaginatedObjectListType

    Pagination:
        1.	LimitOffsetGraphqlPagination
        2.	PageGraphqlPagination
        3.	CursosGraphqlPagination (cooming soon)


### Examples

Here is a simple example of graphene-django-extras usage:

#### 1- Types Definition:

```python
from django.contrib.auth.models import User
from graphene_django_extras import DjangoObjectTypeExtra, DjangoPaginatedObjectListType    
from graphene_django_extras.pagination import LimitOffsetGraphqlPagination

class UserType(DjangoObjectTypeExtra):
    """
        The DjangoObjectTypeExtra have a ID field to filter to avoid resolve method definition on Queries 
    """
    class Meta:
        model = User
        description = "Type for User Model"
        filter_fields = {
            'id': ['exact', ],
            'first_name': ['icontains', 'iexact'],
            'last_name': ['icontains', 'iexact'],
            'username': ['icontains', 'iexact'],
            'email': ['icontains', 'iexact']
        }


class UserListType(DjangoPaginatedObjectListType):
    class Meta:
        description = "User list query definition"
        model = User
        pagination = LimitOffsetGraphqlPagination(page_size=20)
```

#### 2- Input Types can be defined for use on mutations:

```python
from graphene_django_extras import DjangoInputObjectType

class UserInput(DjangoInputObjectType):
    class Meta:
        description = " Input Type for User Model "
        model = User
```

#### 3- You can define traditional mutations that use Input Types or Mutations based on DRF SerializerClass:

```python
import graphene
from graphene_django_extras import DjangoSerializerMutation 
    
from .serializers import UserSerializer
from .types import UserType
from .input_types import UserInputType

class UserSerializerMutation(DjangoSerializerMutation):
    """
        DjangoSerializerMutation autoimplement Create, Delete and Update function
    """
    class Meta:
        description = " Serializer based Mutation for Users "
        serializer_class = UserSerializer


class UserMutation(graphene.mutation):
    """
        You must implement the mutate function
    """

    user = graphene.Field(UserType, required=False)

    class Arguments:
        new_user = graphene.Argument(UserInput)

    class Meta:
        description = "Normal mutation for Users"

    @classmethod
    def mutate(cls, info, **kwargs):
        ...
```

#### 4- Defining the Scheme file:

```python
import graphene
from graphene_django_extras import DjangoObjectField, DjangoListObjectField, DjangoFilterPaginateListField, DjangoFilterListField
from .types import UserType, UserListType
from .mutations import UserMutation, UserSerializerMutation

class Queries(graphene.ObjectType):
    # List of users with separate filter and paginate options
    all_users = DjangoListObjectField(UserListType, description=_('List of users'))
    
    # List of users with filter and paginate options, passing the pagination here
    all_users1 = DjangoFilterPaginateListField(UserType, pagination=LimitOffsetGraphqlPagination())
    
    # List of users with only filter options
    all_users2 = DjangoFilterListField(UserType)
    
    # List of users with only filter options, passing the FilterClass here.
    all_users3 = DjangoListObjectField(UserListType, filterset_class=UserFilter, description=_('All Users query'))

    # Single user queries definitions
    user = DjangoObjectField(UserType, description=_('Single User query'))  
    
    # Other way to define a query to a single user
    other_way_user = DjangoObjectField(UserListType.getOne(), description=_('Other way to query a single User query'))  

class Mutations(graphene.ObjectType):
    user_create = UserSerializerMutation.CreateField(deprecation_reason='Deprecation message')
    user_delete = UserSerializerMutation.DeleteField()
    user_update = UserSerializerMutation.UpdateField()

    traditional_user_mutation = UserMutation.Field()
```

#### 5- Examples of queries:
```js
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
```

#### 6- Examples of Mutations:

```js
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
```
