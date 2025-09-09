# Fields

Graphene-Django-Extras provides several field types for building GraphQL schemas with enhanced functionality.

## DjangoObjectField

Used for single object queries with automatic ID filtering.

```python
from graphene_django_extras import DjangoObjectField
from .types import UserType

class Query(graphene.ObjectType):
    user = DjangoObjectField(UserType, description='Single User query')
```

**Features:**
- Automatic ID-based filtering
- No need to define custom resolve function
- Built-in error handling for non-existent objects

**Usage in GraphQL:**
```graphql
{
  user(id: 1) {
    id
    username
    firstName
  }
}
```

## DjangoFilterListField

Provides filtering capabilities for list queries without pagination.

```python
from graphene_django_extras import DjangoFilterListField
from .types import UserType

class Query(graphene.ObjectType):
    users = DjangoFilterListField(UserType)
```

**Features:**
- Django-filter integration
- Multiple filter types (exact, contains, etc.)
- No pagination (returns all matching results)

**Usage in GraphQL:**
```graphql
{
  users(firstName_Icontains: "john") {
    id
    username
    firstName
    lastName
  }
}
```

## DjangoFilterPaginateListField

Combines filtering and pagination for list queries.

```python
from graphene_django_extras import DjangoFilterPaginateListField
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination
from .types import UserType

class Query(graphene.ObjectType):
    users = DjangoFilterPaginateListField(
        UserType, 
        pagination=LimitOffsetGraphqlPagination(default_limit=20)
    )
```

**Features:**
- All filtering capabilities of DjangoFilterListField
- Built-in pagination support
- Configurable pagination class

**Usage in GraphQL:**
```graphql
{
  users(firstName_Icontains: "john", limit: 10, offset: 0) {
    results {
      id
      username
      firstName
    }
    totalCount
  }
}
```

## DjangoListObjectField

!!! tip "Recommended for Queries"
    This is the most flexible approach for list queries with built-in support for filtering and pagination.

```python
from graphene_django_extras import DjangoListObjectField
from .types import UserListType

class Query(graphene.ObjectType):
    users = DjangoListObjectField(UserListType, description='All Users query')
```

**Features:**
- Works with DjangoListObjectType
- Inherits pagination configuration from the type
- Support for custom FilterSet classes
- Built-in caching support

**Usage in GraphQL:**
```graphql
{
  users(limit: 10, offset: 0) {
    results {
      id
      username
      firstName
    }
    totalCount
  }
}
```

### With Custom FilterSet

```python
import django_filters
from django.contrib.auth.models import User

class UserFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='filter_by_name')
    
    class Meta:
        model = User
        fields = ['username', 'email']
    
    def filter_by_name(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) | Q(last_name__icontains=value)
        )

class Query(graphene.ObjectType):
    users = DjangoListObjectField(
        UserListType, 
        filterset_class=UserFilter,
        description='Users with custom filtering'
    )
```

## Field Comparison

| Feature | DjangoObjectField | DjangoFilterListField | DjangoFilterPaginateListField | DjangoListObjectField |
|---------|------------------|----------------------|------------------------------|----------------------|
| Single Objects | ✅ | ❌ | ❌ | ❌ |
| List Objects | ❌ | ✅ | ✅ | ✅ |
| Filtering | ID only | ✅ | ✅ | ✅ |
| Pagination | ❌ | ❌ | ✅ | ✅ |
| Custom FilterSet | ❌ | ✅ | ✅ | ✅ |
| Type Integration | Basic | Basic | Basic | Full |
| Caching | ❌ | ❌ | ❌ | ✅ |

## Best Practices

### 1. Use DjangoListObjectField for Lists

```python
# ✅ Recommended
class Query(graphene.ObjectType):
    users = DjangoListObjectField(UserListType, description='All users')

# ❌ Less flexible
class Query(graphene.ObjectType):
    users = DjangoFilterPaginateListField(UserType)
```

### 2. Define Filter Fields in Types

```python
class UserType(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = {
            "username": ("exact", "icontains"),
            "email": ("exact", "icontains"),
            "is_active": ("exact",),
        }
```

### 3. Use Descriptive Names

```python
class Query(graphene.ObjectType):
    # ✅ Clear and descriptive
    active_users = DjangoListObjectField(
        UserListType, 
        description='List of active users with pagination'
    )
    
    user_by_id = DjangoObjectField(
        UserType, 
        description='Get a single user by ID'
    )
```

### 4. Combine with Permissions

```python
from graphene_django_extras import DjangoListObjectField

class Query(graphene.ObjectType):
    users = DjangoListObjectField(UserListType)
    
    def resolve_users(self, info, **kwargs):
        if not info.context.user.is_staff:
            raise PermissionError("Staff access required")
        return super().resolve_users(info, **kwargs)
```