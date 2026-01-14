Graphene-Django-Extras
======================

|coverage-status| |python-support| |license| |code-style| |pypi-downloads|

This package adds some extra functionalities to graphene-django to facilitate the graphql use without Relay:

1. Allow pagination and filtering on Queries
2. Allow defining DjangoRestFramework serializers based on Mutations.
3. Allow using Directives on Queries and Fragments.

**NOTE:** Subscription support was moved to `graphene-django-subscriptions <https://github.com/eamigo86/graphene-django-subscriptions>`_

Requirements
------------

- **Python:** 3.12+ (3.13 and 3.14 supported)
- **Django:** 4.0+ (4.2, 5.0, 5.1, 5.2, and 6.0 supported)
- **Graphene-Django:** 3.2+

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code:: bash

    pip install graphene-django-extras

Basic Usage
~~~~~~~~~~~

.. code:: python

    from graphene_django_extras import DjangoListObjectType, DjangoSerializerMutation

    class UserListType(DjangoListObjectType):
        class Meta:
            model = User

    class UserMutation(DjangoSerializerMutation):
        class Meta:
            serializer_class = UserSerializer

Documentation
~~~~~~~~~~~~~

📚 **Full Documentation:** https://eamigo86.github.io/graphene-django-extras/

The complete documentation includes:

- **Installation Guide** - Getting started
- **Quick Start** - Basic setup and examples
- **Usage Guide** - Detailed feature documentation
- **Directives** - GraphQL directives for data formatting
- **API Reference** - Complete API documentation
- **Changelog** - Version history

Key Features
------------

🔍 **Fields**
~~~~~~~~~~~~~
- DjangoObjectField
- DjangoFilterListField
- DjangoFilterPaginateListField
- DjangoListObjectField *(Recommended)*

🧬 **Types**
~~~~~~~~~~~~
- DjangoListObjectType *(Recommended)*
- DjangoInputObjectType
- DjangoSerializerType *(Recommended)*

⚡ **Mutations**
~~~~~~~~~~~~~~~~
- DjangoSerializerMutation *(Recommended)*

📄 **Pagination**
~~~~~~~~~~~~~~~~~~
- LimitOffsetGraphqlPagination
- PageGraphqlPagination

🎯 **Directives**
~~~~~~~~~~~~~~~~~
- String formatting (case, encoding, manipulation)
- Number formatting (currency, math operations)
- Date formatting (with python-dateutil)
- List operations (shuffle, sample)

Configuration
-------------

You can configure global parameters for DjangoListObjectType classes in your settings.py:

.. code:: python

    GRAPHENE_DJANGO_EXTRAS = {
        'DEFAULT_PAGINATION_CLASS': 'graphene_django_extras.paginations.LimitOffsetGraphqlPagination',
        'DEFAULT_PAGE_SIZE': 20,
        'MAX_PAGE_SIZE': 50,
        'CACHE_ACTIVE': True,
        'CACHE_TIMEOUT': 300    # seconds
    }

Examples
--------

Types Definition
~~~~~~~~~~~~~~~~

.. code:: python

    from django.contrib.auth.models import User
    from graphene_django_extras import DjangoListObjectType, DjangoSerializerType
    from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

    class UserListType(DjangoListObjectType):
        class Meta:
            model = User
            pagination = LimitOffsetGraphqlPagination()
            filter_fields = {
                "id": ("exact",),
                "username": ("icontains", "iexact"),
                "email": ("icontains", "iexact"),
            }

Mutations Definition
~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from graphene_django_extras import DjangoSerializerMutation
    from .serializers import UserSerializer

    class UserMutation(DjangoSerializerMutation):
        class Meta:
            serializer_class = UserSerializer

Schema Definition
~~~~~~~~~~~~~~~~~

.. code:: python

    import graphene
    from graphene_django_extras import DjangoObjectField, DjangoListObjectField

    class Query(graphene.ObjectType):
        users = DjangoListObjectField(UserListType)
        user = DjangoObjectField(UserType)

    class Mutation(graphene.ObjectType):
        user_create = UserMutation.CreateField()
        user_update = UserMutation.UpdateField()
        user_delete = UserMutation.DeleteField()

    schema = graphene.Schema(query=Query, mutation=Mutation)

Directives
~~~~~~~~~~

Configure directives in your settings.py:

.. code:: python

    GRAPHENE = {
        'MIDDLEWARE': [
            'graphene_django_extras.ExtraGraphQLDirectiveMiddleware'
        ]
    }

Usage example:

.. code:: python

    from graphene_django_extras import all_directives

    schema = graphene.Schema(
        query=Query,
        mutation=Mutation,
        directives=all_directives
    )

Development
-----------

See our `Development Guide <https://eamigo86.github.io/graphene-django-extras/contributing.html>`_ for contributing guidelines.

License
-------

MIT License - see `LICENSE <https://github.com/eamigo86/graphene-django-extras/blob/master/LICENSE>`_ file for details.

.. references-marker
.. |latest-version| image:: https://img.shields.io/pypi/v/graphene-django-extras.svg
    :target: https://pypi.python.org/pypi/graphene-django-extras/
    :alt: Latest version
.. |coverage-status| image:: https://codecov.io/gh/eamigo86/graphene-django-extras/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/eamigo86/graphene-django-extras
    :alt: Coverage status
.. |python-support| image:: https://img.shields.io/pypi/pyversions/graphene-django-extras.svg
    :target: https://pypi.python.org/pypi/graphene-django-extras
    :alt: Python versions
.. |license| image:: https://img.shields.io/pypi/l/graphene-django-extras.svg
    :target: https://github.com/eamigo86/graphene-django-extras/blob/master/LICENSE
    :alt: Software license
.. |code-style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black
    :alt: Black
.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/graphene-django-extras?style=flat
    :target: https://pypi.python.org/pypi/graphene-django-extras
    :alt: PyPI Downloads
