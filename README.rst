--------------

|Graphene Logo| Graphene-Django-Extras |PyPI version|
===============================================================================

A extra functionalities for `Django <https://www.djangoproject.com/>`__ integration for
`Graphene <http://graphene-python.org/>`__.

Installation
------------

For installing graphene-django-extras, just run this command in your shell:

.. code:: bash

    pip install "graphene-django-extras"

Settings
~~~~~~~~

.. code:: python

    INSTALLED_APPS = (
        # ...
        'graphene_django_extras',
    )    

Urls
~~~~

We need to set up a ``GraphQL`` endpoint in our Django app, so we can
serve the queries.

.. code:: python

    from django.conf.urls import url
    from graphene_django.views import GraphQLView

    urlpatterns = [
        # ...
        url(r'^graphql', GraphQLView.as_view(graphiql=True)),
    ]

Examples
--------

Here is a simple Django model:

.. code:: python

    from django.db import models

    class UserModel(models.Model):
        name = models.CharField(max_length=100)
        last_name = models.CharField(max_length=100)

To create a GraphQL schema for it you simply have to write the
following:

.. code:: python

    from graphene_django import DjangoObjectType
    import graphene

    class User(DjangoObjectType):
        class Meta:
            model = UserModel

    class Query(graphene.ObjectType):
        users = graphene.List(User)

        @graphene.resolve_only_args
        def resolve_users(self):
            return UserModel.objects.all()

    schema = graphene.Schema(query=Query)

Then you can simply query the schema:

.. code:: python

    query = '''
        query {
          users {
            name,
            lastName
          }
        }
    '''
    result = schema.execute(query)

To learn more check out the following `examples <examples/>`__:

-  **Schema with Filtering**: `Cookbook example <examples/cookbook>`__
-  **Relay Schema**: `Starwars Relay example <examples/starwars>`__


Documentation
~~~~~~~~~~~~~


.. |Graphene Logo| image:: http://graphene-python.org/favicon.png
.. |PyPI version| image:: https://badge.fury.io/py/graphene-django.svg
   :target: https://badge.fury.io/py/graphene-django