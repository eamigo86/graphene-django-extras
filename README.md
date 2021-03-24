
---

# Graphene-Django-Extras
![Travis (.org) branch](https://img.shields.io/travis/eamigo86/graphene-django-extras/master)
![Codecov](https://img.shields.io/codecov/c/github/eamigo86/graphene-django-extras)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/graphene-django-extras)
![PyPI](https://img.shields.io/pypi/v/graphene-django-extras?color=blue)
![PyPI - License](https://img.shields.io/pypi/l/graphene-django-extras)
![PyPI - Downloads](https://img.shields.io/pypi/dm/graphene-django-extras?style=flat)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

This package adds some extra functionalities to graphene-django to facilitate the graphql use without Relay:
  1. Allow pagination and filtering on Queries.
  2. Allow defining DjangoRestFramework serializers based on Mutations.
  3. Allow using Directives on Queries and Fragments.

**NOTE:** Subscription support was moved to [graphene-django-subscriptions](https://github.com/eamigo86/graphene-django-subscriptions).

## Installation

For installing graphene-django-extras, just run this command in your shell:

```
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


### Queries and Mutations examples:

This is a basic example of graphene-django-extras package use. You can configure global params
for DjangoListObjectType classes pagination definitions on settings.py like this:

```python
    GRAPHENE_DJANGO_EXTRAS = {
        'DEFAULT_PAGINATION_CLASS': 'graphene_django_extras.paginations.LimitOffsetGraphqlPagination',
        'DEFAULT_PAGE_SIZE': 20,
        'MAX_PAGE_SIZE': 50,
        'CACHE_ACTIVE': True,
        'CACHE_TIMEOUT': 300    # seconds
    }
```

#### 1- Types Definition:

```python
from django.contrib.auth.models import User
from graphene_django_extras import DjangoListObjectType, DjangoSerializerType, DjangoObjectType
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

from .serializers import UserSerializer


class UserType(DjangoObjectType):
    class Meta:
        model = User
        description = " Type definition for a single user "
        filter_fields = {
            "id": ("exact", ),
            "first_name": ("icontains", "iexact"),
            "last_name": ("icontains", "iexact"),
            "username": ("icontains", "iexact"),
            "email": ("icontains", "iexact"),
            "is_staff": ("exact", ),
        }


class UserListType(DjangoListObjectType):
    class Meta:
        description = " Type definition for user list "
        model = User
        pagination = LimitOffsetGraphqlPagination(default_limit=25, ordering="-username") # ordering can be: string, tuple or list


class UserModelType(DjangoSerializerType):
    """ With this type definition it't necessary a mutation definition for user's model """

    class Meta:
        description = " User model type definition "
        serializer_class = UserSerializer
        pagination = LimitOffsetGraphqlPagination(default_limit=25, ordering="-username") # ordering can be: string, tuple or list
        filter_fields = {
            "id": ("exact", ),
            "first_name": ("icontains", "iexact"),
            "last_name": ("icontains", "iexact"),
            "username": ("icontains", "iexact"),
            "email": ("icontains", "iexact"),
            "is_staff": ("exact", ),
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

#### 4- Defining the Schema file:

```python
import graphene
from graphene_django_extras import DjangoObjectField, DjangoListObjectField, DjangoFilterPaginateListField,
DjangoFilterListField, LimitOffsetGraphqlPagination
from .types import UserType, UserListType, UserModelType
from .mutations import UserMutation, UserSerializerMutation


class Queries(graphene.ObjectType):
    # Possible User list queries definitions
    users = DjangoListObjectField(UserListType, description='All Users query')
    users1 = DjangoFilterPaginateListField(UserType, pagination=LimitOffsetGraphqlPagination())
    users2 = DjangoFilterListField(UserType)
    users3 = DjangoListObjectField(UserListType, filterset_class=UserFilter, description='All Users query')

    # Defining a query for a single user
    # The DjangoObjectField have a ID type input field, that allow filter by id and is't necessary to define resolve function
    user = DjangoObjectField(UserType, description='Single User query')

    # Another way to define a query to single user
    user1 = UserListType.RetrieveField(description='User List with pagination and filtering')

    # Exist two ways to define single or list user queries with DjangoSerializerType
    user_retrieve1, user_list1 = UserModelType.QueryFields(
        description='Some description message for both queries',
        deprecation_reason='Some deprecation message for both queries'
    )
    user_retrieve2 = UserModelType.RetrieveField(
        description='Some description message for retrieve query',
        deprecation_reason='Some deprecation message for retrieve query'
    )
    user_list2 = UserModelType.ListField(
        description='Some description message for list query',
        deprecation_reason='Some deprecation message for list query'
    )

class Mutations(graphene.ObjectType):
    user_create = UserSerializerMutation.CreateField(deprecation_reason='Some one deprecation message')
    user_delete = UserSerializerMutation.DeleteField()
    user_update = UserSerializerMutation.UpdateField()

    # Exist two ways to define mutations with DjangoSerializerType
    user_create1, user_delete1, user_update1 = UserModelType.MutationFields(
        description='Some description message for create, delete and update mutations',
        deprecation_reason='Some deprecation message for create, delete and update mutations'
    )

    user_create2 = UserModelType.CreateField(description='Description message for create')
    user_delete2 = UserModelType.DeleteField(description='Description message for delete')
    user_update2 = UserModelType.UpdateField(description='Description message for update')

    traditional_user_mutation = UserMutation.Field()
```

#### 5- Directives settings:
For use Directives you must follow two simple steps:
1. You must add **'graphene_django_extras.ExtraGraphQLDirectiveMiddleware'** to your GRAPHENE dict
config on your settings.py:

```python
# settings.py

GRAPHENE = {
    'SCHEMA_INDENT': 4,
    'MIDDLEWARE': [
        'graphene_django_extras.ExtraGraphQLDirectiveMiddleware'
    ]
}
```

2. You must add the *directives* param with your custom directives to your schema definition. This module comes with
some common directives for you, these directives allow to you format strings, numbers, lists, and dates (optional), and
you can load like this:

```python
# schema.py
from graphene_django_extras import all_directives

schema = graphene.Schema(
    query=RootQuery,
    mutation=RootMutation,
    directives=all_directives
)
```
**NOTE**: Date directive depends on *dateutil* module, so if you do not have installed it, this directive will not be
available. You can install *dateutil* module manually:
```
pip install python-dateutil
```
or like this:
```
pip install graphene-django-extras[date]
```
That's all !!!


#### 6- Complete Directive list:

##### FOR NUMBERS:
1. **FloorGraphQLDirective**: Floors value. Supports both String and Float fields.
2. **CeilGraphQLDirective**: Ceils value. Supports both String and Float fields.

##### FOR LIST:
1. **ShuffleGraphQLDirective**: Shuffle the list in place.
2. **SampleGraphQLDirective**: Take a 'k' int argument and return a k length list of unique elements chosen from the
taken list

##### FOR DATE:
1. **DateGraphQLDirective**: Take a optional 'format' string argument and format the date from resolving the field by
dateutil module with the 'format' format. Default format is: 'DD MMM YYYY HH:mm:SS' equivalent to
'%d %b %Y %H:%M:%S' python format.

##### FOR STRING:
1. **DefaultGraphQLDirective**: Take a 'to' string argument. Default to given value if None or ""
2. **Base64GraphQLDirective**: Take a optional ("encode" or "decode") 'op' string argument(default='encode').
Encode or decode the string taken.
3. **NumberGraphQLDirective**: Take a 'as' string argument. String formatting like a specify Python number formatting.
4. **CurrencyGraphQLDirective**: Take a optional 'symbol' string argument(default="$").
Prepend the *symbol* argument to taken string and format it like a currency.
5. **LowercaseGraphQLDirective**: Lowercase the taken string.
6. **UppercaseGraphQLDirective**: Uppercase the taken string.
7. **CapitalizeGraphQLDirective**: Return the taken string with its first character capitalized and the rest lowered.
8. **CamelCaseGraphQLDirective**: CamelCase the taken string.
9. **SnakeCaseGraphQLDirective**: SnakeCase the taken string.
10. **KebabCaseGraphQLDirective**: SnakeCase the taken string.
11. **SwapCaseGraphQLDirective**: Return the taken string with uppercase characters converted to lowercase and vice
versa.
12. **StripGraphQLDirective**: Take a optional 'chars' string argument(default=" ").
Return the taken string with the leading and trailing characters removed. The 'chars' argument is not a prefix or
suffix; rather, all combinations of its values are stripped.
13. **TitleCaseGraphQLDirective**: Return the taken string title-cased, where words start with an uppercase character
and the remaining characters are lowercase.
14. **CenterGraphQLDirective**: Take a 'width' string argument and a optional 'fillchar' string argument(default=" ").
Return the taken string centered with the 'width' argument as new length. Padding is done using the specified
'fillchar' argument. The original string is returned if 'width' argument is less than or equal to taken string
length.
15. **ReplaceGraphQLDirective**: Take two strings arguments 'old' and 'new', and a optional integer argument
'count'.
Return the taken string with all occurrences of substring 'old' argument replaced by 'new' argument value.
If the optional argument 'count' is given, only the first 'count' occurrences are replaced.


#### 7- Queries's examples:
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

#### 8- Mutations's examples:

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

#### 9- Directives's examples:
Let's suppose that we have this query:
```js
query{
    allUsers{
        result{
            id
            firstName
            lastName
            dateJoined
            lastLogin
        }
    }
}
```
And return this data:
```js
{
  "data": {
    "allUsers": {
      "results": [
        {
            "id": "1",
            "firstName": "JOHN",
            "lastName": "",
            "dateJoined": "2017-06-20 09:40:30",
            "lastLogin": "2017-08-05 21:05:02"
        },
        {
            "id": "2",
            "firstName": "Golden",
            "lastName": "GATE",
            "dateJoined": "2017-01-02 20:36:45",
            "lastLogin": "2017-06-20 10:15:31"
        },
        {
            "id": "3",
            "firstName": "Nike",
            "lastName": "just do it!",
            "dateJoined": "2017-08-30 16:05:20",
            "lastLogin": "2017-12-05 09:23:09"
        }
      ]
    }
  }
}
```
As we see, some data it's missing or just not have the format that we like it, so let's go to format the output data
that we desired:
```js
query{
    allUsers{
        result{
            id
            firstName @capitalize
            lastName @default(to: "Doe") @title_case
            dateJoined @date(format: "DD MMM YYYY HH:mm:SS")
            lastLogin @date(format: "time ago")
        }
    }
}
```
And we get this output data:
```js
{
  "data": {
    "allUsers": {
      "results": [
        {
            "id": "1",
            "firstName": "John",
            "lastName": "Doe",
            "dateJoined": "20 Jun 2017 09:40:30",
            "lastLogin": "4 months, 12 days, 15 hours, 27 minutes and 58 seconds ago"
        },
        {
            "id": "2",
            "firstName": "Golden",
            "lastName": "Gate",
            "dateJoined": "02 Jan 2017 20:36:45",
            "lastLogin": "5 months, 28 days, 2 hours, 17 minutes and 53 seconds ago"
        },
        {
            "id": "3",
            "firstName": "Nike",
            "lastName": "Just Do It!",
            "dateJoined": "30 Aug 2017 16:05:20",
            "lastLogin": "13 days, 3 hours, 10 minutes and 31 seconds ago"
        }
      ]
    }
  }
}
```
As we see, the directives are an easy way to format output data on queries, and it's can be put together like a chain.

**List of possible date's tokens**:
"YYYY", "YY", "WW", "W", "DD", "DDDD", "d", "ddd", "dddd", "MM", "MMM", "MMMM", "HH", "hh", "mm", "ss", "A", "ZZ", "z".

You can use this shortcuts too:

1. "time ago"
2. "iso": "YYYY-MMM-DDTHH:mm:ss"
3. "js" or "javascript": "ddd MMM DD YYYY HH:mm:ss"


## Change Log:

#### v0.5.1:
    1. Update dependencies

#### v0.5.0:
    1. Upgrade to graphene v3

#### v0.4.8:
    1. Upgrade graphene-django dependency to version == 2.6.0.

#### v0.4.6:
    1. Upgrade graphql-core dependency to version >= 2.2.1.
    2. Upgrade graphene dependency to version >= 2.1.8.
    3. Upgrade graphene-django dependency to version >= 2.5.0.
    4. Upgrade django-filter dependency to version >= 2.2.0.
    5. Fixed bug 'DjangoSerializerOptions' object has no attribute 'interfaces' after update to graphene==2.1.8.
    6. The tests were refactored and added some extra tests for DjangoSerializerType.

#### v0.4.5:
    1. Fixed compatibilities issues to use graphene-django>=2.3.2.
    2. Improved code quality and use Black code format.
    3. Fixed minor bug with "time ago" date directive.

#### v0.3.7:
    1. Improved DjangoListType and DjangoObjectType to share the filterset_class between the two class.

#### v0.3.6:
    1. Improve DjangoSerializerMutation resolvers.

#### v0.3.5:
    1. Fixed minor bug on ExtraGraphQLDirectiveMiddleware.
    2. Fixed error with DRF 3.8 Compatibility.
    3. Updated List's Fields to pass info.context to filterset as request, this allow filtering by request data.
    4. Added new feature to ordering paginated queries.

#### v0.3.4-alpha2:
    1. Fixed minor bug on DjangoListObjectType.

#### v0.3.4-alpha1:
    1. Added filterset_class to the listing types as default filter.
    2. Changed getOne by RetrieveField on DjangoListObjectType.

####  v0.3.3:
    1. Added filterset_class to DjangoObjectType.
    2. Fixed minor bug on factory_types function.

####  v0.3.3-alpha1:
    1. Fixed minor bug on *queryset_factory* function.

#### v0.3.2:
    1. Updated Date directive format function for better string format combinations.
    2. Updated custom Time, Date and DateTime base types to be used with Date directive.
    3. Fixed bug with caching Introspection queries on ExtraGraphQLView.

#### v0.3.1:
    1. Fixed bug with default Date directive format.

#### v0.3.0:
    1. Added Binary graphql type. A BinaryArray is used to convert a Django BinaryField to the string form.
    2. Added 'CACHE_ACTIVE' and 'CACHE_TIMEOUT' config options to GRAPHENE_DJANGO_EXTRAS settings for activate cache and
     define a expire time. Default values are: CACHE_ACTIVE=False, CACHE_TIMEOUT=300 (seconds). Only available for
     Queries.
    3. Updated Date directive for use with Django TimeField, DateField, and DateTimeField.
    4. Updated ExtraGraphQLView and AuthenticatedGraphQLView to allow use subscription requests on graphene-django >=2.0
    5. Updated setup dependence to graphene-django>=2.0.

#### v0.2.2:
    1. Fixed performance bug on some queries when request nested ManyToMany fields.

#### v0.2.1:
    1. Fixed bug with default PaginationClass and DjangoFilterPaginateListField.

#### v0.2.0:
    1. Added some useful directives to use on queries and fragments.
    2. Fixed error on DjangoFilterPaginateListField resolve function.

#### v0.1.6:
    1. Fixed bug on create and update function on serializer mutation.

#### v0.1.3:
    1. Fixed minors  bugs.

#### v0.1.2:
    1. Added ok field and errors field to DjangoSerializerType like on DjangoSerializerMutation.
    2. Added possibility of filtering in those queries fields that return a list of objects.
    3. Updated DRF compatibility.
    4. Fixed bug with filters when use global DEFAULT_PAGINATION_CLASS.

#### v0.1.1:
    1. Fixed error with JSONField reference on Django==1.8.x installations.

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
    1.  Fixed bug when subscribing to a given action (create, update or delete).
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
