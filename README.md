
---

# Graphene-Django-Extras [![PyPI version](https://badge.fury.io/py/graphene-django-extras.svg)](https://badge.fury.io/py/graphene-django-extras)


This package add some extra functionalities to graphene-django to facilitate the graphql use without Relay:
  1. Allows pagination and filtering on Queries.
  2. Allows to define DjangoRestFramework serializers based Mutations.

**NOTE:** Subscription support was moved to [graphene-django-subscriptions](https://github.com/eamigo86/graphene-django-subscriptions) due incompatibility with subscriptions on graphene-django>=2.0

## Installation

For installing graphene-django-extras, just run this command in your shell:

```bash
pip install graphene-django-extras
```

## Documentation:

### Extra functionalities:
 **Fields:**
  1.  DjangoObjectField
  2.  DjangoFilterListField
  3.  DjangoFilterPaginateListField
  4.  DjangoListObjectField (*Recommended for Queries definition*)

 **Mutations:**
  1.  DjangoSerializerMutation (*Recommended for Mutations definition*)

 **Types:**
  1.  DjangoListObjectType  (*Recommended for Types definition*)
  2.  DjangoInputObjectType
  3.  DjangoSerializerType  (*Recommended for quick queries and mutations definitions*)

 **Paginations:**
  1.  LimitOffsetGraphqlPagination
  2.  PageGraphqlPagination
  3.  CursorGraphqlPagination (*coming soon*)


### Queries and Mutations examples:

This is a basic example of graphene-django-extras package use. You can configure global params
for DjangoListObjectType classes pagination definitions on settings.py like this:

```python
    GRAPHENE_DJANGO_EXTRAS = {
        'DEFAULT_PAGINATION_CLASS': 'graphene_django_extras.paginations.LimitOffsetGraphqlPagination',
        'DEFAULT_PAGE_SIZE': 20,
        'MAX_PAGE_SIZE': 50,
    }
```

#### 1- Types Definition:

```python
from django.contrib.auth.models import User
from graphene_django import DjangoObjectType
from graphene_django_extras import DjangoListObjectType, DjangoSerializerType
from graphene_django_extras.pagination import LimitOffsetGraphqlPagination

from .serializers import UserSerializer


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
        pagination = LimitOffsetGraphqlPagination(page_size=20)


class UserModelType(DjangoSerializerType):
    """ With this type definition it't necessary a mutation definition for user's model """

    class Meta:
        description = " User's model type definition "
        serializer_class = UserSerializer
        pagination = LimitOffsetGraphqlPagination(default_limit=25)
        filter_fields = {
            'id': ['exact', ],
            'first_name': ['icontains', 'iexact'],
            'last_name': ['icontains', 'iexact'],
            'username': ['icontains', 'iexact'],
            'email': ['icontains', 'iexact'],
            'is_staff': ['exact']
        }
```

#### 2- You can to define InputTypes for use on mutations:

```python
from graphene_django_extras import DjangoInputObjectType


class UserInput(DjangoInputObjectType):
    class Meta:
        description = " User InputType definition to use as input on an Arguments class on traditional Mutations "
        model = User
```

#### 3- You can define traditional mutations that use InputTypes or Mutations based on DRF serializers:

```python
import graphene
from graphene_django_extras import DjangoSerializerMutation

from .serializers import UserSerializer
from .types import UserType
from .input_types import UserInputType


class UserSerializerMutation(DjangoSerializerMutation):
    """
        DjangoSerializerMutation auto implement Create, Delete and Update functions
    """
    class Meta:
        description = " DRF serializer based Mutation for Users "
        serializer_class = UserSerializer


class UserMutation(graphene.Mutation):
    """
         On traditional mutation classes definition you must implement the mutate function
    """

    user = graphene.Field(UserType, required=False)

    class Arguments:
        new_user = graphene.Argument(UserInput)

    class Meta:
        description = " Graphene traditional mutation for Users "

    @classmethod
    def mutate(cls, root, info, *args, **kwargs):
        ...
```

#### 4- Defining the Scheme file:

```python
import graphene
from graphene_django_extras import DjangoObjectField, DjangoListObjectField, DjangoFilterPaginateListField,
DjangoFilterListField, LimitOffsetGraphqlPagination
from .types import UserType, UserListType, UserModelType
from .mutations import UserMutation, UserSerializerMutation


class Queries(graphene.ObjectType):
    # Possible User list queries definitions
    all_users = DjangoListObjectField(UserListType, description=_('All Users query'))
    all_users1 = DjangoFilterPaginateListField(UserType, pagination=LimitOffsetGraphqlPagination())
    all_users2 = DjangoFilterListField(UserType)
    all_users3 = DjangoListObjectField(UserListType, filterset_class=UserFilter, description=_('All Users query'))

    # Defining a query for a single user
    # The DjangoObjectField have a ID type input field, that allow filter by id and is't necessary to define resolve function
    user = DjangoObjectField(UserType, description=_('Single User query'))

    # Another way to define a query to single user
    user1 = DjangoObjectField(UserListType.getOne(), description=_('User list with pagination and filtering'))

    # Exist two ways to define single or list user queries with DjangoSerializerType
    user_retrieve1, user_list1 = UserModelType.QueryFields(description='Some description message for both queries',
                                                           deprecation_reason='Some deprecation message for both queries')
    user_retrieve2 = UserModelType.RetrieveField(description='Some description message for retrieve query',
                                                 deprecation_reason='Some deprecation message for retrieve query')
    user_list2 = UserModelType.ListField(description='Some description message for list query',
                                         deprecation_reason='Some deprecation message for list query')

class Mutations(graphene.ObjectType):
    user_create = UserSerializerMutation.CreateField(deprecation_reason='Some one deprecation message')
    user_delete = UserSerializerMutation.DeleteField()
    user_update = UserSerializerMutation.UpdateField()

    # Exist two ways to define mutations with DjangoSerializerType
    user_create1, user_delete1, user_update1 = UserModelType.MutationFields(
        description='Some description message for create, delete and update mutations',
        deprecation_reason='Some deprecation message for create, delete and update mutations')

    user_create2 = UserModelType.CreateField(description='Description message for create')
    user_delete2 = UserModelType.DeleteField(description='Description message for delete')
    user_update2 = UserModelType.UpdateField(description='Description message for update')

    traditional_user_mutation = UserMutation.Field()
```

#### 5- Queries's examples:
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

  user1(id:2){
    id
    username
    firstName
  }
}
```

#### 6- Mutations's examples:

```js
mutation{
  userCreate(newUser:{username:"test", password:"test*123"}){
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

## Change Log:

#### v0.1.0:
    1. Added DjangoSerializerType for quick Django's models types definition (See documentation).
    2. Moved support for Subscriptions to graphene-django-subscriptions packages for
    incompatibility with graphene-django>=2.0.
    3. Fixed bug on DjangoFilterPaginateListField's pagination.

#### v0.1.0-alpha12:
    1. Added new settings param: MAX_PAGE_SIZE, to use on GRAPHENE_DJANGO_EXTRAS
    configuration dict for better customize DjangoListObjectType's pagination.
    2. Added support to Django's field: GenericRel.
    3. Improve model's fields calculation for to add all possible related and reverse fields.
    4. Improved documentation translation.

#### v0.1.0-alpha11:
    1. Improved ordering for showed fields on graphqli's IDE.
    2. Added better descriptions for auto generated fields.

#### v0.1.0-alpha10:
    1. Improve converter.py file to avoid create field for auto generate OneToOneField
    product of an inheritance.
    2. Fixed bug in Emun generation for fields with choices of model inheritance child.

#### v0.1.0-alpha9:
    1. Fixed bug on GenericType and GenericInputType generations for
    Queries list Type and Mutations.

#### v0.1.0-alpha6:
    1. Fixed with exclude fields and converter function.

#### v0.1.0-alpha5:
    1. Updated dependencies to graphene-django>=2.0.
    2. Fixed minor bugs on queryset_builder performance.

#### v0.1.0-alpha4:
    1.  Add queryset options to DjangoListObjectType Meta class for specify wanted model queryset.
    2.  Add AuthenticatedGraphQLView on graphene_django_extras.views for use
    'permission', 'authorization' and 'throttle' classes based on the DRF settings. Special thanks to
    [@jacobh](https://github.com/jacobh) for this
    [comment](https://github.com/graphql-python/graphene/issues/249#issuecomment-300068390)

#### v0.1.0-alpha3:
    1.  Fixed bug on subscriptions when not specified any field in "data" parameter to bean return on notification
    message.

#### v0.1.0-alpha2:
    1.  Fixed bug when subscribing to a given action (create, update pr delete).
    2.  Added intuitive and simple web tool to test notifications of graphene-django-extras subscription.

#### v0.1.0-alpha1:
    1.  Added support to multiselect choices values for models.CharField with choices attribute,
    on queries and mutations. Example: Integration with django-multiselectfield package.
    2.  Added support to GenericForeignKey and GenericRelation fields, on queries and mutations.
    3.  Added first approach to support Subscriptions with Channels, with subscribe and unsubscribe operations.
    Using channels-api package.
    4.  Fixed minors bugs.

#### v0.0.4:
    1. Fix error on DateType encode.

#### v0.0.3:
    1. Implement custom implementation of DateType for use converter and avoid error on Serializer Mutation.

#### v0.0.2:
    1. Changed dependency of DRF to 3.6.4 on setup.py file, to avoid an import error produced by some changes in
    new version of DRF=3.7.0 and because DRF 3.7.0 dropped support to Django versions < 1.10.

#### v0.0.1:
    1. Fixed bug on DjangoInputObjectType class that refer to unused interface attribute.
    2. Added support to create nested objects like in
    [DRF](http://www.django-rest-framework.org/api-guide/serializers/#writable-nested-representations),
    it's valid to SerializerMutation and DjangoInputObjectType, only is necessary to specify nested_fields=True
    on its Meta class definition.
    3. Added support to show, only in mutations types to create objects and with debug=True on settings,
    inputs autocomplete ordered by required fields first.
    4. Fixed others minors bugs.

#### v0.0.1-rc.2:
    1. Make queries pagination configuration is more friendly.

#### v0.0.1-rc.1:
    1. Fixed a bug with input fields in the converter function.

#### v0.0.1-beta.10:
    1. Fixed bug in the queryset_factory function because it did not always return a queryset.

#### v0.0.1-beta.9:
    1. Remove hard dependence with psycopg2 module.
    2. Fixed bug that prevented use queries with fragments.
    3. Fixed bug relating to custom django_filters module and ordering fields.

#### v0.0.1-beta.6:
    1. Optimizing imports, fix some minors bugs and working on performance.

#### v0.0.1-beta.5:
    1. Repair conflict on converter.py, by the use of get_related_model function with: OneToOneRel,
    ManyToManyRel and ManyToOneRel.

#### v0.0.1-beta.4:
    1. First commit.
