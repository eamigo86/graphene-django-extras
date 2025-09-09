# Graphene-Django-Extras

![Codecov](https://img.shields.io/codecov/c/github/eamigo86/graphene-django-extras)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/graphene-django-extras)
![PyPI](https://img.shields.io/pypi/v/graphene-django-extras?color=blue)
![PyPI - License](https://img.shields.io/pypi/l/graphene-django-extras)
![PyPI - Downloads](https://img.shields.io/pypi/dm/graphene-django-extras?style=flat)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

This package adds some extra functionalities to graphene-django to facilitate the graphql use without Relay:

  1. Allow pagination and filtering on Queries
  2. Allow defining DjangoRestFramework serializers based on Mutations.
  3. Allow using Directives on Queries and Fragments.

**NOTE:** Subscription support was moved to [graphene-django-subscriptions](https://github.com/eamigo86/graphene-django-subscriptions).

## Quick Start

### Installation

```bash
pip install graphene-django-extras
```

### Basic Usage

```python
from graphene_django_extras import DjangoListObjectType, DjangoSerializerMutation

class UserListType(DjangoListObjectType):
    class Meta:
        model = User

class UserMutation(DjangoSerializerMutation):
    class Meta:
        serializer_class = UserSerializer
```

## Documentation

📚 **[Full Documentation](https://eamigo86.github.io/graphene-django-extras/)**

The complete documentation includes:

- **[Installation Guide](https://eamigo86.github.io/graphene-django-extras/installation.html)** - Getting started
- **[Quick Start](https://eamigo86.github.io/graphene-django-extras/quickstart.html)** - Basic setup and examples
- **[Usage Guide](https://eamigo86.github.io/graphene-django-extras/usage/index.html)** - Detailed feature documentation
- **[Directives](https://eamigo86.github.io/graphene-django-extras/directives.html)** - GraphQL directives for data formatting
- **[API Reference](https://eamigo86.github.io/graphene-django-extras/api/index.html)** - Complete API documentation
- **[Changelog](https://eamigo86.github.io/graphene-django-extras/changelog.html)** - Version history

## Key Features

### 🔍 **Fields**
- DjangoObjectField
- DjangoFilterListField
- DjangoFilterPaginateListField
- DjangoListObjectField *(Recommended)*

### 🧬 **Types**
- DjangoListObjectType *(Recommended)*
- DjangoInputObjectType
- DjangoSerializerType *(Recommended)*

### ⚡ **Mutations**
- DjangoSerializerMutation *(Recommended)*

### 📄 **Pagination**
- LimitOffsetGraphqlPagination
- PageGraphqlPagination

### 🎯 **Directives**
- String formatting (case, encoding, manipulation)
- Number formatting (currency, math operations)
- Date formatting (with python-dateutil)
- List operations (shuffle, sample)

## Development

See our [Development Guide](https://eamigo86.github.io/graphene-django-extras/contributing.html) for contributing guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.
