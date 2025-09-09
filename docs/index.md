# Graphene-Django-Extras Documentation

![Codecov](https://img.shields.io/codecov/c/github/eamigo86/graphene-django-extras){ .md-badge }
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/graphene-django-extras){ .md-badge }
![PyPI](https://img.shields.io/pypi/v/graphene-django-extras?color=blue){ .md-badge }
![PyPI - License](https://img.shields.io/pypi/l/graphene-django-extras){ .md-badge }
![PyPI - Downloads](https://img.shields.io/pypi/dm/graphene-django-extras?style=flat){ .md-badge }
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg){ .md-badge }

This package adds some extra functionalities to graphene-django to facilitate the graphql use without Relay:

1. **Allow pagination and filtering on Queries**
2. **Allow defining DjangoRestFramework serializers based on Mutations**
3. **Allow using Directives on Queries and Fragments**

!!! note "Subscription Support"
    Subscription support was moved to [graphene-django-subscriptions](https://github.com/eamigo86/graphene-django-subscriptions).

## Key Features

### 🔍 Fields
- **DjangoObjectField** - Single object queries with automatic ID filtering
- **DjangoFilterListField** - List queries with filtering
- **DjangoFilterPaginateListField** - List queries with filtering and pagination
- **DjangoListObjectField** - :material-star: *Recommended for Queries*

### 🧬 Types
- **DjangoListObjectType** - :material-star: *Recommended for Types*
- **DjangoInputObjectType** - Input types for mutations
- **DjangoSerializerType** - :material-star: *Recommended for quick setup*

### ⚡ Mutations
- **DjangoSerializerMutation** - :material-star: *Recommended for Mutations*

### 📄 Pagination
- **LimitOffsetGraphqlPagination** - Offset-based pagination
- **PageGraphqlPagination** - Page-based pagination

### 🎯 Directives
- **String formatting** - Case transformation, encoding, manipulation
- **Number formatting** - Currency, mathematical operations
- **Date formatting** - Custom date formats with python-dateutil
- **List operations** - Shuffle, sample operations

## Quick Example

```python title="Basic Usage"
from graphene_django_extras import (
    DjangoListObjectType, 
    DjangoSerializerMutation,
    LimitOffsetGraphqlPagination
)

class UserListType(DjangoListObjectType):
    class Meta:
        model = User
        pagination = LimitOffsetGraphqlPagination(default_limit=25)

class UserMutation(DjangoSerializerMutation):
    class Meta:
        serializer_class = UserSerializer
```

## Getting Started

Ready to dive in? Check out our [Installation Guide](installation.md) to get started, or jump straight to the [Quick Start](quickstart.md) for a hands-on tutorial.

## Community & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/eamigo86/graphene-django-extras/issues)
- **PyPI Package**: [Install from PyPI](https://pypi.org/project/graphene-django-extras/)
- **Source Code**: [View on GitHub](https://github.com/eamigo86/graphene-django-extras)