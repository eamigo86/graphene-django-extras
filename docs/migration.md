# Migration Guide

This guide helps you migrate between major versions of graphene-django-extras.

## Migrating from v0.x to v1.0

### Breaking Changes

#### 1. Django Version Support

!!! warning "Django Version Requirements"
    Django versions < 3.2 are no longer supported. Please upgrade to Django 3.2+ before upgrading to graphene-django-extras v1.0.

**Before (v0.x):**
```python
# Supported Django 1.11, 2.0, 2.1, 2.2, 3.0, 3.1, 3.2+
```

**After (v1.0):**
```python
# Only supports Django 3.2, 4.0, 4.2, 5.0, 5.1
```

#### 2. Python Version Support

**Before (v0.x):**
```python
# Supported Python 3.6, 3.7, 3.8, 3.9
```

**After (v1.0):**
```python
# Only supports Python 3.10, 3.11, 3.12
```

#### 3. Graphene Version

**Before (v0.x):**
```python
# Used graphene v2.x
```

**After (v1.0):**
```python
# Uses graphene v3.x
```

### Code Changes Required

#### 1. Import Changes

Most imports remain the same, but some internal APIs have changed:

```python
# These imports remain the same ✅
from graphene_django_extras import (
    DjangoListObjectType,
    DjangoSerializerMutation,
    DjangoObjectField,
    LimitOffsetGraphqlPagination
)
```

#### 2. Schema Definition Changes

**Before (v0.x):**
```python
import graphene
from graphene_django_extras import all_directives

schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    directives=all_directives  # Old way
)
```

**After (v1.0):**
```python
import graphene
from graphene_django_extras import all_directives

schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    directives=all_directives  # Still works the same way
)
```

#### 3. FilterSet Compatibility

Due to django-filter updates, you may need to adjust your custom FilterSets:

**Before (v0.x):**
```python
class UserFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(name='username')  # Old syntax
```

**After (v1.0):**
```python
class UserFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='username')  # New syntax
```

#### 4. Pagination Changes

The pagination API remains mostly the same, but performance has been improved:

```python
# This works the same in both versions ✅
class UserListType(DjangoListObjectType):
    class Meta:
        model = User
        pagination = LimitOffsetGraphqlPagination(default_limit=25)
```

### Migration Steps

#### Step 1: Update Dependencies

1. **Update your requirements:**

```bash
# Update your requirements.txt or pyproject.toml
pip install 'graphene-django-extras>=1.0.0'
pip install 'Django>=3.2'
pip install 'python>=3.10'
```

2. **Test your current implementation:**

```bash
python manage.py test
```

#### Step 2: Update Django (if needed)

If you're on Django < 3.2, follow Django's official migration guide:

1. Upgrade to Django 3.2 first
2. Run migrations and tests
3. Then upgrade graphene-django-extras

#### Step 3: Update Python (if needed)

If you're on Python < 3.10:

1. Upgrade to Python 3.10+
2. Update your virtual environment
3. Reinstall dependencies

#### Step 4: Test GraphQL Queries

Test your GraphQL endpoint to ensure everything works:

```graphql
# Test a basic query
{
  users(limit: 5) {
    results {
      id
      username
    }
    totalCount
  }
}

# Test a mutation
mutation {
  userCreate(newUser: {username: "test"}) {
    ok
    errors {
      field
      messages
    }
  }
}
```

### Performance Improvements in v1.0

#### 1. Better Query Optimization

v1.0 includes improved query optimization for pagination:

```python
# Automatically optimized in v1.0
class UserListType(DjangoListObjectType):
    class Meta:
        model = User
        queryset = User.objects.select_related('profile')  # Better performance
```

#### 2. Improved Filtering

Enhanced filtering with better lookup support:

```python
class UserType(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = {
            "username": ("exact", "icontains", "istartswith"),  # More options
            "email": ("exact", "icontains"),
            "date_joined": ("exact", "gte", "lte", "year", "month"),  # Enhanced
        }
```

### Troubleshooting Common Issues

#### Issue 1: Import Errors

**Error:**
```
ImportError: cannot import name 'SomeClass' from 'graphene_django_extras'
```

**Solution:**
Check if the class still exists in v1.0. Most classes remain the same, but some internal classes may have been refactored.

#### Issue 2: Django Compatibility

**Error:**
```
Django version X.X is not supported
```

**Solution:**
Upgrade Django to version 3.2 or higher.

#### Issue 3: Filter Field Errors

**Error:**
```
TypeError: __init__() got an unexpected keyword argument 'name'
```

**Solution:**
Update FilterSet field definitions to use `field_name` instead of `name`:

```python
# Change this
name = django_filters.CharFilter(name='username')

# To this
name = django_filters.CharFilter(field_name='username')
```

### Getting Help

If you encounter issues during migration:

1. Check the [changelog](changelog.md) for detailed changes
2. Review the [examples](usage/examples.md) for updated syntax
3. Open an issue on [GitHub](https://github.com/eamigo86/graphene-django-extras/issues)

### Migration Checklist

- [ ] Updated Python to 3.10+
- [ ] Updated Django to 3.2+
- [ ] Updated graphene-django-extras to v1.0+
- [ ] Updated FilterSet syntax (if using custom filters)
- [ ] Tested all GraphQL queries
- [ ] Tested all GraphQL mutations
- [ ] Ran full test suite
- [ ] Updated documentation/comments in code

!!! success "Migration Complete"
    Once you've completed these steps, you should be successfully running graphene-django-extras v1.0 with improved performance and compatibility!