
Graphene-Django-Extras
======================

This package add some extra functionalities to **graphene-django** to facilitate the graphql use without Relay:
  1. Allow pagination and filtering on Queries.
  2. Allow to define DjangoRestFramework serializers based Mutations.
  3. Add support to Subscription's requests and its integration with websockets using **Channels** package.

Installation:
-------------

For installing graphene-django-extras, just run this command in your shell:

.. code:: bash

    pip install "graphene-django-extras"

Documentation:
--------------

**********************
Extra functionalities:
**********************
  **Fields:**
    1. DjangoObjectField
    2. DjangoFilterListField
    3. DjangoFilterPaginateListField
    4. DjangoListObjectField  (Recommended for Queries definition)

  **Mutations:**
    1.	DjangoSerializerMutation  (Recommended for Mutations definition)

  **Types:**
    1.	DjangoListObjectType  (Recommended for Types definition)
    2.	DjangoInputObjectType

  **Paginations:**
    1.	LimitOffsetGraphqlPagination
    2.	PageGraphqlPagination
    3.	CursorGraphqlPagination (coming soon)

  **Subscriptions:**
    1.  Subscription  (Abstract class to define subscriptions to a DjangoSerializerMutation)
    2.  GraphqlAPIDemultiplexer  (Custom WebSocket consumer subclass that handles demultiplexing streams)

Queries and Mutations examples:
-------------------------------

This is a basic example of graphene-django-extras package use:

********************
1- Types Definition:
********************


.. code:: python

    from django.contrib.auth.models import User
    from graphene_django import DjangoObjectType
    from graphene_django_extras import DjangoListObjectType
    from graphene_django_extras.pagination import LimitOffsetGraphqlPagination


    class UserType(DjangoObjectType):
        class Meta:
            model = User
            description = " Type definition for a single user object "
            filter_fields = {
                'id': ['exact', ],
                'first_name': ['icontains', 'iexact'],
                'last_name': ['icontains', 'iexact'],
                'username': ['icontains', 'iexact'],
                'email': ['icontains', 'iexact']
            }


    class UserListType(DjangoListObjectType):
        class Meta:
            description = " Type definition for users objects list "
            model = User
            pagination = LimitOffsetGraphqlPagination()


***************************************************
2- InputTypes can be defined for use on mutations:
***************************************************

.. code:: python

    from graphene_django_extras import DjangoInputObjectType


    class UserInput(DjangoInputObjectType):
        class Meta:
            description = " User Input Type for used as input on Arguments classes on traditional Mutations "
            model = User


**********************
3- Defining Mutations:
**********************

You can define traditional mutations that use Input Types or Mutations based on DRF SerializerClass:


.. code:: python

    import graphene
    from .serializers import UserSerializer
    from graphene_django_extras import DjangoSerializerMutation
    from .types import UserType
    from .input_types import UserInputType


    class UserSerializerMutation(DjangoSerializerMutation):
        """
            DjangoSerializerMutation auto implement Create, Delete and Update functions
        """
        class Meta:
            description = " Serializer based Mutation for Users "
            serializer_class = UserSerializer


    class UserMutation(graphene.Mutation):
        """
            On traditional mutation classes definition you must implement the mutate function
        """

        user = graphene.Field(UserType, required=False)

        class Arguments:
            new_user = graphene.Argument(UserInput)

        class Meta:
            description = " Traditional graphene mutation for Users "

        @classmethod
        def mutate(cls, root, info, *args, **kwargs):
            ...


********************
4- Defining schemes:
********************

.. code:: python

    import graphene
    from graphene_django_extras import DjangoObjectField, DjangoListObjectField, DjangoFilterPaginateListField, DjangoFilterListField, LimitOffsetGraphqlPagination
    from .types import UserType, UserListType
    from .mutations import UserMutation, UserSerializerMutation


    class Queries(graphene.ObjectType):
        # Possible User list queries definitions
        all_users = DjangoListObjectField(UserListType, description=_('All Users query'))
        all_users1 = DjangoFilterPaginateListField(UserType, pagination=LimitOffsetGraphqlPagination())
        all_users2 = DjangoFilterListField(UserType)
        all_users3 = DjangoListObjectField(UserListType, filterset_class=UserFilter, description=_('All Users query'))

        # Defining a query for a single user
        # The DjangoObjectField have a ID input field, that allow filter by id and is't necessary resolve method definition
        user = DjangoObjectField(UserType, description=_('Single User query'))

        # Another way to define a single user query
        user1 = DjangoObjectField(UserListType.getOne(), description=_('User List with pagination and filtering'))


    class Mutations(graphene.ObjectType):
        user_create = UserSerializerMutation.CreateField(deprecation_reason='Some deprecation message')
        user_delete = UserSerializerMutation.DeleteField()
        user_update = UserSerializerMutation.UpdateField()

        traditional_user_mutation = UserMutation.Field()


***********************
5- Examples of queries:
***********************

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

        user1(id:2){
            id
            username
            firstName
        }
    }


*************************
6- Examples of Mutations:
*************************

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

Subscriptions:
--------------

This first approach to support Graphql subscriptions with Channels in graphene-django-extras, use channels-api package.

*****************************************
1- Defining custom Subscriptions classes:
*****************************************

You must to have defined a DjangoSerializerMutation class for each model that you want to define a Subscription class:

.. code:: python

    # app/graphql/subscriptions.py
    import graphene
    from graphene_django_extras.subscription import Subscription
    from .mutations import UserMutation, GroupMutation


    class UserSubscription(Subscription):
        class Meta:
            mutation_class = UserMutation
            stream = 'users'
            description = 'Subscription for users'


    class GroupSubscription(Subscription):
        class Meta:
            mutation_class = GroupMutation
            stream = 'groups'
            description = 'Subscriptions for groups'


Add ours subscriptions definitions into our app schema:

.. code:: python

    # app/graphql/schema.py
    import graphene
    from .subscriptions import UserSubscription, GroupSubscription


    class Subscriptions(graphene.ObjectType):
        user_subscription = UserSubscription.Field()
        GroupSubscription = PersonSubscription.Field()


Add your app schema into your project root schema:

.. code:: python

    # schema.py
    import graphene
    import custom.app.route.graphql.schema


    class RootQuery(custom.app.route.graphql.schema.Query, graphene.ObjectType):
        class Meta:
            description = 'Root Queries for my Project'


    class RootSubscription(custom.app.route.graphql.schema.Mutation, graphene.ObjectType):
        class Meta:
            description = 'Root Mutations for my Project'


    class RootSubscription(custom.app.route.graphql.schema.Subscriptions, graphene.ObjectType):
        class Meta:
            description = 'Root Subscriptions for my Project'


    schema = graphene.Schema(
        query=RootQuery,
        mutation=RootMutation,
        subscription=RootSubscription
    )


********************************************************
2- Defining Channels settings and custom routing config:
********************************************************
**Note**: For more information about this step see Channels documentation.

You must to have defined a DjangoSerializerMutation class for each model that you want to define a Subscription class:


.. code:: python

    # app/routing.py
    from graphene_django_extras.subscriptions import GraphqlAPIDemultiplexer
    from channels.routing import route_class
    from .graphql.subscriptions import UserSubscription, GroupSubscription


    class CustomAppDemultiplexer(GraphqlAPIDemultiplexer):
        consumers = {
          'users': UserSubscription.get_binding().consumer,
          'groups': GroupSubscription.get_binding().consumer
        }


    app_routing = [
        route_class(CustomAppDemultiplexer)
    ]


Defining our project routing, like custom root project urls:

.. code:: python

    # project/routing.py
    from channels import include

    project_routing = [
        include("custom.app.folder.routing.app_routing", path=r"^/custom_websocket_path"),
    ]


You should add channels and channels_api modules into your INSTALLED_APPS setting and you must defining your routing project definition into the CHANNEL_LAYERS setting:

.. code:: python

    # settings.py
    ...
    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        ...
        'channels',
        'channels_api',

        'custom_app'
    )

    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "asgiref.inmemory.ChannelLayer",
            "ROUTING": "myproject.routing.project_routing",  # Our project routing
        },
    }
    ...


*****************************
3- Examples of Subscriptions:
*****************************

In your client you must define websocket connection to: 'ws://host:port/custom_websocket_path'.
When the connection is established, the server return a websocket message like this:
{"channel_id": "GthKdsYVrK!WxRCdJQMPi", "connect": "success"}, where you must store the channel_id value to later use in your graphql subscriptions request for subscribe or unsubscribe operations.
The Subscription accept five possible parameters:

1.  **operation**: Operation to perform: subscribe or unsubscribe. (required)
2.  **action**: Action you wish to subscribe: create, update, delete or all_actions. (required)
3.  **channelId**: Websocket connection identification. (required)
4.  **id**: ID field value of model object that you wish to subscribe to. (optional)
5.  **data**: List of desired model fields that you want in subscription's  notification. (optional)

.. code:: python

    subscription{
        userSubscription(
            action: UPDATE,
            operation: SUBSCRIBE,
            channelId: "GthKdsYVrK!WxRCdJQMPi",
            id: 5,
            data: [ID, USERNAME, FIRST_NAME, LAST_NAME, EMAIL, IS_SUPERUSER]
        ){
            ok
            error
            stream
        }
    }


In this case, the subscription request sanded return a websocket message to client like this: *{"action": "update", "operation": "subscribe", "ok": true, "stream": "users", "error": null}* and each time than the user with id=5 get modified, you will receive a message through websocket's connection with the following format:

.. code:: python

    {
        "stream": "users",
        "payload": {
            "action": "update",
            "model": "auth.user",
            "data": {
                "id": 5,
                "username": "meaghan90",
                "first_name": "Meaghan",
                "last_name": "Ackerman",
                "email": "meaghan@gmail.com",
                "is_superuser": false
            }
        }
    }


For unsubscribe you must send a graphql subscription request like this:

.. code:: python

    subscription{
        userSubscription(
            action: UPDATE,
            operation: UNSUBSCRIBE,
            channelId: "GthKdsYVrK!WxRCdJQMPi",
            id: 5
        ){
            ok
            error
            stream
        }
    }


*NOTE*: Each time than the Graphql server restart, you must to reestablish the websocket's connection and resend the subscription graphql request with a new websocket connection id.


Change Log:
-----------

**************
v0.1.0-alpha9:
**************
1. Fixed bug on GenericType and GenericInputType generations for Queries list Type and Mutations.

**************
v0.1.0-alpha6:
**************
1. Fixed with exclude fields and converter function.

**************
v0.1.0-alpha5:
**************
1. Updated to graphene-django>=2.0.
2. Fixed minor bugs on queryset_builder performance.

**************
v0.1.0-alpha4:
**************
1.  Add **queryset** options to **DjangoListObjectType** Meta class for specify wanted model queryset.
2.  Add AuthenticatedGraphQLView on graphene_django_extras.views for use 'permission', 'authorization' and 'throttle' classes based on the DRF settings. Special thanks to `@jacobh <https://github.com/jacobh>`_ for this `comment <https://github.com/graphql-python/graphene/issues/249#issuecomment-300068390>`_.

**************
v0.1.0-alpha3:
**************
1.  Fixed bug on subscriptions when not specified any field in "data" parameter to bean return on
notification message.

**************
v0.1.0-alpha2:
**************
1.  Fixed bug when subscribing to a given action (create, update pr delete).
2.  Added intuitive and simple web tool to test notifications of graphene-django-extras subscription.

**************
v0.1.0-alpha1:
**************
1.  Added support to multiselect choices values for models.CharField with choices attribute, on queries and mutations. Example: Integration with django-multiselectfield package.
2.  Added support to GenericForeignKey and GenericRelation fields, on queries and mutations.
3.  Added first approach to support Subscriptions with **Channels**, with subscribe and unsubscribe operations. Using **channels-api** package.
4.  Fixed minors bugs.

*******
v0.0.4:
*******
1. Fix error on DateType encode.

*******
v0.0.3:
*******
1. Implement custom implementation of DateType for use converter and avoid error on Serializer Mutation.

*******
v0.0.2:
*******
1. Changed dependency of DRF to 3.6.4 on setup.py file, to avoid an import error produced by some changes in new version of DRF=3.7.0 and because DRF 3.7.0 dropped support to Django versions < 1.10.

*******
v0.0.1:
*******
1. Fixed bug on DjangoInputObjectType class that refer to unused interface attribute.
2. Added support to create nested objects like in `DRF <http://www.django-rest-framework.org/api-guide/serializers/#writable-nested-representations>`, it's valid to SerializerMutation and DjangoInputObjectType, only is necessary to specify nested_fields=True on its Meta class definition.
3. Added support to show, only in mutations types to create objects and with debug=True on settings, inputs autocomplete ordered by required fields first.
4. Fixed others minors bugs.

************
v0.0.1-rc.2:
************
1. Make queries pagination configuration is more friendly.

************
v0.0.1-rc.1:
************
1. Fixed a bug with input fields in the converter function.

***************
v0.0.1-beta.10:
***************
1. Fixed bug in the queryset_factory function because it did not always return a queryset.

**************
v0.0.1-beta.9:
**************
1. Remove hard dependence with psycopg2 module.
2. Fixed bug that prevented use queries with fragments.
3. Fixed bug relating to custom django_filters module and ordering fields.

**************
v0.0.1-beta.6:
**************
1. Optimizing imports, fix some minors bugs and working on performance.

**************
v0.0.1-beta.5:
**************
1. Repair conflict on converter.py, by the use of get_related_model function with: OneToOneRel, ManyToManyRel and ManyToOneRel.

**************
v0.0.1-beta.4:
**************
1. First commit