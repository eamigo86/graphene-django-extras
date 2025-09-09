# Types

Graphene-Django-Extras provides enhanced type classes that extend the basic graphene-django functionality.

## DjangoListObjectType

!!! tip "Recommended for Types"
    Extends DjangoObjectType with built-in pagination and filtering support.

```python
from graphene_django_extras import DjangoListObjectType
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination
from django.contrib.auth.models import User

class UserListType(DjangoListObjectType):
    class Meta:
        description = "Type definition for user list"
        model = User
        pagination = LimitOffsetGraphqlPagination(
            default_limit=25,
            ordering="-date_joined"
        )
        filter_fields = {
            "username": ("exact", "icontains"),
            "email": ("exact", "icontains"),
            "is_active": ("exact",),
        }
```

### Features

- **Built-in Pagination**: Automatic pagination with configurable settings
- **Filtering**: Integrated django-filter support
- **Ordering**: Custom ordering options
- **Caching**: Optional query result caching
- **Custom Queryset**: Override default queryset behavior

### Configuration Options

```python
class UserListType(DjangoListObjectType):
    class Meta:
        model = User
        description = "User list with advanced features"

        # Pagination
        pagination = LimitOffsetGraphqlPagination(
            default_limit=20,
            max_limit=100,
            ordering=("-date_joined", "username")
        )

        # Filtering
        filter_fields = {
            "username": ("exact", "icontains", "istartswith"),
            "email": ("exact", "icontains"),
            "date_joined": ("exact", "gte", "lte"),
            "is_active": ("exact",),
            "groups": ("exact",),
        }

        # Custom queryset
        queryset = User.objects.select_related('profile')

        # Field restrictions
        fields = ("id", "username", "email", "first_name", "last_name")
        exclude = ("password",)
```

### Helper Methods

```python
class Query(graphene.ObjectType):
    # Get both list and retrieve fields
    users = UserListType.ListField(description="List all users")
    user = UserListType.RetrieveField(description="Get single user")
```

## DjangoInputObjectType

Creates input types for mutations based on Django models.

```python
from graphene_django_extras import DjangoInputObjectType
from django.contrib.auth.models import User

class UserInput(DjangoInputObjectType):
    class Meta:
        description = "User input for mutations"
        model = User
        fields = ("username", "email", "first_name", "last_name")
        # or exclude specific fields
        # exclude = ("password", "date_joined", "last_login")
```

### Advanced Configuration

```python
import graphene
from graphene_django_extras import DjangoInputObjectType

class UserCreateInput(DjangoInputObjectType):
    """Input for creating new users"""

    # Add custom fields
    confirm_password = graphene.String(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password")
        description = "Input type for user creation"

class UserUpdateInput(DjangoInputObjectType):
    """Input for updating existing users"""

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")
        description = "Input type for user updates"
```

### Usage in Mutations

```python
class CreateUserMutation(graphene.Mutation):
    class Arguments:
        input = UserCreateInput(required=True)

    user = graphene.Field(UserType)
    success = graphene.Boolean()

    def mutate(self, info, input):
        # Access input fields
        username = input.username
        email = input.email
        # ... mutation logic
```

## DjangoSerializerType

!!! tip "Recommended for Quick Setup"
    Automatically generates types, queries, and mutations based on DRF serializers.

```python
from graphene_django_extras import DjangoSerializerType
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination
from .serializers import UserSerializer

class UserModelType(DjangoSerializerType):
    class Meta:
        description = "User model type with auto-generated operations"
        serializer_class = UserSerializer
        pagination = LimitOffsetGraphqlPagination(
            default_limit=25,
            ordering="-date_joined"
        )
        filter_fields = {
            "username": ("exact", "icontains"),
            "email": ("exact", "icontains"),
            "is_active": ("exact",),
        }
```

### Auto-generated Query Fields

```python
class Query(graphene.ObjectType):
    # Generate both retrieve and list queries automatically
    user_retrieve, user_list = UserModelType.QueryFields(
        description='User queries',
        deprecation_reason='Optional deprecation message'
    )

    # Or define them separately
    user_detail = UserModelType.RetrieveField(
        description='Get single user by ID'
    )
    user_list_custom = UserModelType.ListField(
        description='List users with filtering and pagination'
    )
```

### Auto-generated Mutation Fields

```python
class Mutation(graphene.ObjectType):
    # Generate all CRUD mutations
    user_create, user_delete, user_update = UserModelType.MutationFields(
        description='User CRUD operations'
    )

    # Or define them separately
    create_user = UserModelType.CreateField(description='Create new user')
    delete_user = UserModelType.DeleteField(description='Delete user')
    update_user = UserModelType.UpdateField(description='Update user')
```

### Serializer Integration

```python
# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

# The DjangoSerializerType will automatically use these fields
class UserModelType(DjangoSerializerType):
    class Meta:
        serializer_class = UserSerializer
```

## Type Comparison

| Feature | DjangoListObjectType | DjangoInputObjectType | DjangoSerializerType |
|---------|---------------------|----------------------|---------------------|
| **Purpose** | List queries with pagination | Input for mutations | Complete CRUD operations |
| **Pagination** | ✅ Built-in | ❌ N/A | ✅ Built-in |
| **Filtering** | ✅ Built-in | ❌ N/A | ✅ Built-in |
| **Auto Queries** | Manual setup | ❌ N/A | ✅ Auto-generated |
| **Auto Mutations** | ❌ No | ❌ N/A | ✅ Auto-generated |
| **Serializer Integration** | ❌ No | ❌ No | ✅ Full integration |
| **Customization** | High | High | Medium |
| **Setup Complexity** | Medium | Low | Low |

## Best Practices

### 1. Choose the Right Type

```python
# ✅ For list queries with custom logic
class UserListType(DjangoListObjectType):
    class Meta:
        model = User

# ✅ For input validation
class UserInput(DjangoInputObjectType):
    class Meta:
        model = User
        fields = ("username", "email")

# ✅ For rapid prototyping
class UserModelType(DjangoSerializerType):
    class Meta:
        serializer_class = UserSerializer
```

### 2. Use Descriptive Names

```python
# ✅ Clear naming
class UserListType(DjangoListObjectType): pass
class CreateUserInput(DjangoInputObjectType): pass
class UserCRUDType(DjangoSerializerType): pass

# ❌ Confusing naming
class UserType(DjangoListObjectType): pass  # Is it single or list?
class UserInput(DjangoSerializerType): pass  # Not an input type
```

### 3. Optimize Performance

```python
class UserListType(DjangoListObjectType):
    class Meta:
        model = User
        # Optimize database queries
        queryset = User.objects.select_related('profile').prefetch_related('groups')

        # Limit exposed fields
        fields = ("id", "username", "email", "first_name", "last_name")

        # Enable caching for expensive queries
        # (Configure in settings)
```

### 4. Combine Types Strategically

```python
# Use DjangoSerializerType for basic CRUD
class UserModelType(DjangoSerializerType):
    class Meta:
        serializer_class = UserSerializer

# Use DjangoListObjectType for complex list logic
class UserAnalyticsType(DjangoListObjectType):
    total_posts = graphene.Int()

    class Meta:
        model = User

    def resolve_total_posts(self, info):
        return self.posts.count()

# Use DjangoInputObjectType for complex input validation
class UserRegistrationInput(DjangoInputObjectType):
    confirm_password = graphene.String(required=True)
    terms_accepted = graphene.Boolean(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password")
```
