# Types API Reference

This section provides detailed API documentation for GraphQL type classes in `graphene-django-extras`.

## DjangoObjectType

Enhanced Django model GraphQL type with filtering and pagination support.

```python
class DjangoObjectType(ObjectType)
```

### Meta Configuration

The `DjangoObjectType` is configured through a nested `Meta` class:

```python
class UserType(DjangoObjectType):
    class Meta:
        model = User
        only_fields = ('id', 'username', 'email')
        filter_fields = {'username': ('exact', 'icontains')}
```

### Meta Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | `Model` | Required | Django model class |
| `registry` | `Registry` | Global registry | Type registry instance |
| `skip_registry` | `bool` | `False` | Skip automatic type registration |
| `only_fields` | `tuple/list` | `()` | Include only specified fields |
| `exclude_fields` | `tuple/list` | `()` | Exclude specified fields |
| `include_fields` | `tuple/list` | `()` | Additional fields to include |
| `filter_fields` | `dict` | `None` | Field filtering configuration |
| `interfaces` | `tuple` | `()` | GraphQL interfaces to implement |
| `filterset_class` | `FilterSet` | `None` | Custom FilterSet class |

### Methods

#### `resolve_id(info)`

Resolve the ID field for the object.

**Returns:** Primary key value of the model instance

#### `is_type_of(root, info)` (classmethod)

Check if the root object is of this type.

**Parameters:**
- `root` (`Any`): Object to check
- `info` (`ResolveInfo`): GraphQL resolve info

**Returns:** `bool` - True if object matches this type

#### `get_queryset(queryset, info)` (classmethod)

Override to customize the queryset used for this type.

**Parameters:**
- `queryset` (`QuerySet`): Base queryset
- `info` (`ResolveInfo`): GraphQL resolve info

**Returns:** Modified `QuerySet`

#### `get_node(info, id)` (classmethod)

Get a single node by ID.

**Parameters:**
- `info` (`ResolveInfo`): GraphQL resolve info
- `id` (`Any`): Object identifier

**Returns:** Model instance or `None`

### Example Usage

=== "Basic Type"

    ```python
    from graphene_django_extras import DjangoObjectType
    from .models import User

    class UserType(DjangoObjectType):
        class Meta:
            model = User
            description = "User account type"
    ```

=== "With Filtering"

    ```python
    class UserType(DjangoObjectType):
        class Meta:
            model = User
            filter_fields = {
                'username': ('exact', 'icontains'),
                'email': ('exact', 'icontains'),
                'is_active': ('exact',),
                'date_joined': ('gte', 'lte'),
            }
    ```

=== "Field Control"

    ```python
    class UserType(DjangoObjectType):
        class Meta:
            model = User
            only_fields = ('id', 'username', 'email', 'first_name', 'last_name')
            # Alternative: exclude_fields = ('password', 'user_permissions')
    ```

=== "Custom Queryset"

    ```python
    class UserType(DjangoObjectType):
        class Meta:
            model = User

        @classmethod
        def get_queryset(cls, queryset, info):
            return queryset.select_related('profile').prefetch_related('posts')
    ```

---

## DjangoInputObjectType

Django model GraphQL input type for mutations and arguments.

```python
class DjangoInputObjectType(InputObjectType)
```

### Meta Configuration

Configure input types through the `Meta` class:

```python
class UserInput(DjangoInputObjectType):
    class Meta:
        model = User
        input_for = 'create'
        only_fields = ('username', 'email', 'first_name', 'last_name')
```

### Meta Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | `Model` | Required | Django model class |
| `registry` | `Registry` | Global registry | Type registry instance |
| `skip_registry` | `bool` | `False` | Skip automatic registration |
| `only_fields` | `tuple/list` | `()` | Include only specified fields |
| `exclude_fields` | `tuple/list` | `()` | Exclude specified fields |
| `filter_fields` | `dict` | `None` | Field filtering configuration |
| `input_for` | `str` | `'create'` | Input purpose: 'create', 'update', or 'delete' |
| `nested_fields` | `tuple/dict` | `()` | Nested field configuration |
| `container` | `type` | Auto-generated | Container class for the input type |

### Methods

#### `get_type()` (classmethod)

Get the type when the unmounted type is mounted.

**Returns:** The input type class

### Example Usage

=== "Create Input"

    ```python
    from graphene_django_extras import DjangoInputObjectType

    class UserCreateInput(DjangoInputObjectType):
        class Meta:
            model = User
            input_for = 'create'
            only_fields = ('username', 'email', 'first_name', 'last_name', 'password')
    ```

=== "Update Input"

    ```python
    class UserUpdateInput(DjangoInputObjectType):
        class Meta:
            model = User
            input_for = 'update'
            exclude_fields = ('password', 'date_joined')
    ```

=== "With Nested Fields"

    ```python
    class UserInput(DjangoInputObjectType):
        class Meta:
            model = User
            input_for = 'create'
            nested_fields = {
                'profile': 'ProfileInput',
                'addresses': 'AddressInput'
            }
    ```

---

## DjangoListObjectType

GraphQL type for paginated lists of Django objects with count and results.

```python
class DjangoListObjectType(ObjectType)
```

### Meta Configuration

Configure list types with pagination and filtering:

```python
class UserListType(DjangoListObjectType):
    class Meta:
        model = User
        pagination = LimitOffsetGraphqlPagination(default_limit=25)
```

### Meta Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | `Model` | Required | Django model class |
| `description` | `str` | Auto-generated | Type description |
| `results_field_name` | `str` | `'results'` | Name of results field |
| `pagination` | `BaseDjangoGraphqlPagination` | `None` | Pagination configuration |
| `filter_fields` | `dict` | `None` | Field filtering configuration |
| `filterset_class` | `FilterSet` | `None` | Custom FilterSet class |

### Generated Fields

A `DjangoListObjectType` automatically generates these fields:

| Field | Type | Description |
|-------|------|-------------|
| `count` | `Int` | Total number of objects |
| `results` | `List[ObjectType]` | Paginated list of objects |

### Methods

#### `ListField(**kwargs)` (classmethod)

Create a field for this list type.

**Parameters:**
- `**kwargs`: Additional field arguments

**Returns:** `DjangoListObjectField` instance

#### `RetrieveField(**kwargs)` (classmethod)

Create a field for retrieving a single object from this list type.

**Parameters:**
- `**kwargs`: Additional field arguments

**Returns:** `DjangoObjectField` instance

#### `get_queryset(queryset, info)` (classmethod)

Customize the base queryset for the list.

**Parameters:**
- `queryset` (`QuerySet`): Base queryset
- `info` (`ResolveInfo`): GraphQL resolve info

**Returns:** Modified `QuerySet`

### Example Usage

=== "Basic List Type"

    ```python
    from graphene_django_extras import (
        DjangoListObjectType,
        LimitOffsetGraphqlPagination
    )

    class UserListType(DjangoListObjectType):
        class Meta:
            model = User
            description = "Paginated list of users"
            pagination = LimitOffsetGraphqlPagination(default_limit=20)
    ```

=== "With Custom Pagination"

    ```python
    from graphene_django_extras import PageGraphqlPagination

    class PostListType(DjangoListObjectType):
        class Meta:
            model = Post
            pagination = PageGraphqlPagination(
                page_size=15,
                page_size_query_param='pageSize'
            )
            filter_fields = {
                'title': ('icontains',),
                'status': ('exact',),
                'author__username': ('icontains',),
            }
    ```

=== "With Custom Queryset"

    ```python
    class UserListType(DjangoListObjectType):
        class Meta:
            model = User
            pagination = LimitOffsetGraphqlPagination(default_limit=25)

        @classmethod
        def get_queryset(cls, queryset, info):
            return queryset.filter(is_active=True).select_related('profile')
    ```

=== "Schema Integration"

    ```python
    import graphene
    from graphene_django_extras import DjangoListObjectField

    class Query(graphene.ObjectType):
        all_users = DjangoListObjectField(UserListType)

        # Or use the shorthand method
        users = UserListType.ListField()
        user = UserListType.RetrieveField()

    schema = graphene.Schema(query=Query)
    ```

### GraphQL Response Structure

```json
{
  "data": {
    "allUsers": {
      "count": 150,
      "results": [
        {
          "id": "1",
          "username": "john_doe",
          "email": "john@example.com"
        },
        {
          "id": "2",
          "username": "jane_smith",
          "email": "jane@example.com"
        }
      ]
    }
  }
}
```

---

## DjangoSerializerType

GraphQL type based on Django REST Framework serializers.

```python
class DjangoSerializerType(ObjectType)
```

### Meta Configuration

Configure serializer types with automatic CRUD operations:

```python
class UserSerializerType(DjangoSerializerType):
    class Meta:
        serializer_class = UserSerializer
        pagination = LimitOffsetGraphqlPagination(default_limit=25)
```

### Meta Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `serializer_class` | `Serializer` | Required | DRF Serializer class |
| `model` | `Model` | From serializer | Django model class |
| `pagination` | `BaseDjangoGraphqlPagination` | Default | Pagination configuration |
| `filter_fields` | `dict` | `None` | Field filtering configuration |
| `filterset_class` | `FilterSet` | `None` | Custom FilterSet class |
| `description` | `str` | Auto-generated | Type description |

### Generated Methods

#### `QueryFields(**kwargs)` (classmethod)

Generate both single object and list query fields.

**Returns:** Tuple of (`single_field`, `list_field`)

#### `ListField(**kwargs)` (classmethod)

Create a list field for this serializer type.

**Returns:** `DjangoListObjectField` instance

#### `RetrieveField(**kwargs)` (classmethod)

Create a retrieve field for single objects.

**Returns:** `DjangoObjectField` instance

### Example Usage

=== "Basic Serializer Type"

    ```python
    from graphene_django_extras import DjangoSerializerType
    from .serializers import UserSerializer

    class UserSerializerType(DjangoSerializerType):
        class Meta:
            serializer_class = UserSerializer
            description = "User type based on serializer"
    ```

=== "With Pagination and Filtering"

    ```python
    from .filtersets import UserFilterSet

    class UserSerializerType(DjangoSerializerType):
        class Meta:
            serializer_class = UserSerializer
            pagination = LimitOffsetGraphqlPagination(default_limit=30)
            filterset_class = UserFilterSet
    ```

=== "Schema Integration"

    ```python
    import graphene

    class Query(graphene.ObjectType):
        # Generate both fields automatically
        user, users = UserSerializerType.QueryFields()

        # Or create individual fields
        user_list = UserSerializerType.ListField()
        single_user = UserSerializerType.RetrieveField()

    schema = graphene.Schema(query=Query)
    ```

---

## Type Registration

All types are automatically registered in a global registry for reuse and relationship resolution.

### Registry Operations

```python
from graphene_django_extras.registry import get_global_registry

# Get the global registry
registry = get_global_registry()

# Check if a type is registered
user_type = registry.get_type_for_model(User)

# Register a type manually
registry.register(CustomUserType)
```

### Custom Registry

```python
from graphene_django_extras import Registry

# Create custom registry
custom_registry = Registry()

class UserType(DjangoObjectType):
    class Meta:
        model = User
        registry = custom_registry
```

## Advanced Usage

### Custom Field Resolvers

```python
import graphene

class UserType(DjangoObjectType):
    full_name = graphene.String()
    post_count = graphene.Int()

    class Meta:
        model = User

    def resolve_full_name(self, info):
        return f"{self.first_name} {self.last_name}"

    def resolve_post_count(self, info):
        return self.posts.count()
```

### Dynamic Field Generation

```python
class UserType(DjangoObjectType):
    class Meta:
        model = User

    @classmethod
    def __init_subclass_with_meta__(cls, **options):
        # Add dynamic fields before calling super
        cls.custom_field = graphene.String()
        super().__init_subclass_with_meta__(**options)
```

### Performance Optimization

```python
class UserType(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = {
            'username': ('exact', 'icontains'),
            'email': ('exact',),
        }

    @classmethod
    def get_queryset(cls, queryset, info):
        # Optimize queries with select_related and prefetch_related
        return queryset.select_related(
            'profile'
        ).prefetch_related(
            'posts',
            'posts__comments'
        )
```

## Error Handling

### Type Validation

```python
class UserType(DjangoObjectType):
    class Meta:
        model = User

    @classmethod
    def is_type_of(cls, root, info):
        # Custom type checking logic
        if hasattr(root, 'user_type'):
            return root.user_type == 'standard'
        return super().is_type_of(root, info)
```

### Field Resolution Errors

```python
class UserType(DjangoObjectType):
    avatar_url = graphene.String()

    class Meta:
        model = User

    def resolve_avatar_url(self, info):
        try:
            if self.profile and self.profile.avatar:
                return self.profile.avatar.url
            return None
        except AttributeError:
            return None
```

## Best Practices

!!! tip "Type Best Practices"

    1. **Use Descriptive Names**: Choose clear, descriptive type names
    2. **Control Field Exposure**: Use `only_fields` or `exclude_fields` appropriately
    3. **Optimize Queries**: Implement `get_queryset` for performance optimization
    4. **Handle Null Values**: Always handle potential null values in resolvers
    5. **Document Types**: Provide meaningful descriptions for types and fields
    6. **Separate Concerns**: Use different input types for different operations

### Security Considerations

```python
class UserType(DjangoObjectType):
    class Meta:
        model = User
        # Don't expose sensitive fields
        exclude_fields = (
            'password', 'user_permissions',
            'groups', 'is_superuser'
        )

    @classmethod
    def get_queryset(cls, queryset, info):
        # Apply security filters
        if not info.context.user.is_staff:
            return queryset.filter(is_active=True)
        return queryset
```

This comprehensive API reference covers all type classes in `graphene-django-extras`, providing developers with the knowledge needed to effectively create and customize GraphQL types for their Django applications.
