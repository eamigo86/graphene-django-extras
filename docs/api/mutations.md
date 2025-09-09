# Mutations API Reference

This section provides detailed API documentation for mutation classes in `graphene-django-extras`.

## DjangoSerializerMutation

The primary mutation class that provides automatic CRUD operations based on Django REST Framework serializers.

```python
class DjangoSerializerMutation(ObjectType)
```

### Meta Configuration

Configure mutations through a nested `Meta` class:

```python
class UserMutation(DjangoSerializerMutation):
    class Meta:
        serializer_class = UserSerializer
        description = "User CRUD operations"
```

### Meta Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `serializer_class` | `Serializer` | Required | Django REST Framework serializer |
| `only_fields` | `tuple/list` | `()` | Include only specified fields |
| `exclude_fields` | `tuple/list` | `()` | Exclude specified fields |
| `include_fields` | `tuple/list` | `()` | Additional fields to include |
| `input_field_name` | `str` | `'new_{model}'` | Name of input argument |
| `output_field_name` | `str` | `'{model}'` | Name of output field |
| `description` | `str` | Auto-generated | Mutation description |
| `nested_fields` | `dict` | `{}` | Nested field serializers |

### Fields

Every `DjangoSerializerMutation` includes these standard fields:

| Field | Type | Description |
|-------|------|-------------|
| `ok` | `Boolean` | Success indicator |
| `errors` | `List[ErrorType]` | Validation errors |
| `{model_name}` | `ObjectType` | The created/updated/deleted object |

### Class Methods

#### `__init_subclass_with_meta__(**kwargs)` (classmethod)

Initialize the mutation subclass with meta configuration.

**Parameters:**
- `serializer_class` (`Serializer`): Required DRF serializer
- `only_fields` (`tuple`): Fields to include
- `exclude_fields` (`tuple`): Fields to exclude
- `include_fields` (`tuple`): Additional fields
- `input_field_name` (`str`): Input argument name
- `output_field_name` (`str`): Output field name
- `description` (`str`): Mutation description
- `nested_fields` (`dict`): Nested field configuration

#### `get_errors(errors)` (classmethod)

Create error response with provided errors.

**Parameters:**
- `errors` (`list`): List of error objects

**Returns:** Mutation instance with errors

#### `perform_mutate(obj, info)` (classmethod)

Create successful mutation response.

**Parameters:**
- `obj` (`Model`): The model instance
- `info` (`ResolveInfo`): GraphQL resolve info

**Returns:** Mutation instance with success response

#### `get_serializer_kwargs(root, info, **kwargs)` (classmethod)

Override to provide custom serializer initialization arguments.

**Parameters:**
- `root` (`Any`): Root object
- `info` (`ResolveInfo`): GraphQL resolve info
- `**kwargs`: Additional arguments

**Returns:** `dict` of serializer kwargs

#### `manage_nested_fields(data, root, info)` (classmethod)

Process nested field data for the mutation.

**Parameters:**
- `data` (`dict`): Input data
- `root` (`Any`): Root object
- `info` (`ResolveInfo`): GraphQL resolve info

**Returns:** Processed nested objects or error response

### CRUD Operations

#### `create(root, info, **kwargs)` (classmethod)

Create a new object using the provided data.

**Parameters:**
- `root` (`Any`): Root object
- `info` (`ResolveInfo`): GraphQL resolve info
- `**kwargs`: Mutation arguments including input data

**Returns:** Mutation response with created object or errors

#### `update(root, info, **kwargs)` (classmethod)

Update an existing object with provided data.

**Parameters:**
- `root` (`Any`): Root object
- `info` (`ResolveInfo`): GraphQL resolve info
- `**kwargs`: Mutation arguments including input data

**Returns:** Mutation response with updated object or errors

#### `delete(root, info, **kwargs)` (classmethod)

Delete an object by its ID.

**Parameters:**
- `root` (`Any`): Root object
- `info` (`ResolveInfo`): GraphQL resolve info
- `**kwargs`: Mutation arguments including object ID

**Returns:** Mutation response with deleted object or errors

#### `save(serialized_obj, root, info, **kwargs)` (classmethod)

Save serialized object after validation.

**Parameters:**
- `serialized_obj` (`Serializer`): Validated serializer instance
- `root` (`Any`): Root object
- `info` (`ResolveInfo`): GraphQL resolve info
- `**kwargs`: Additional arguments

**Returns:** Tuple of `(success: bool, result: object or errors)`

### Field Generation Methods

#### `CreateField(*args, **kwargs)` (classmethod)

Create a GraphQL field for create mutations.

**Returns:** `Field` instance configured for create operations

#### `UpdateField(*args, **kwargs)` (classmethod)

Create a GraphQL field for update mutations.

**Returns:** `Field` instance configured for update operations

#### `DeleteField(*args, **kwargs)` (classmethod)

Create a GraphQL field for delete mutations.

**Returns:** `Field` instance configured for delete operations

#### `MutationFields(*args, **kwargs)` (classmethod)

Get all mutation fields (create, delete, update).

**Returns:** Tuple of `(create_field, delete_field, update_field)`

### Example Usage

=== "Basic Mutation"

    ```python
    from graphene_django_extras import DjangoSerializerMutation
    from .serializers import UserSerializer

    class UserMutation(DjangoSerializerMutation):
        class Meta:
            serializer_class = UserSerializer
            description = "User CRUD operations"
    ```

=== "With Field Control"

    ```python
    class UserMutation(DjangoSerializerMutation):
        class Meta:
            serializer_class = UserSerializer
            exclude_fields = ('password', 'is_staff', 'is_superuser')
            input_field_name = 'user_data'
            output_field_name = 'user'
    ```

=== "With Nested Fields"

    ```python
    class UserMutation(DjangoSerializerMutation):
        class Meta:
            serializer_class = UserSerializer
            nested_fields = {
                'profile': ProfileSerializer,
                'addresses': AddressSerializer
            }
    ```

=== "Custom Arguments"

    ```python
    import graphene

    class UserMutation(DjangoSerializerMutation):
        class Meta:
            serializer_class = UserSerializer

        class Arguments:
            send_email = graphene.Boolean(
                default_value=False,
                description="Send welcome email"
            )

        @classmethod
        def get_serializer_kwargs(cls, root, info, **kwargs):
            return {
                'context': {
                    'request': info.context,
                    'send_email': kwargs.get('send_email', False)
                }
            }
    ```

=== "Custom Validation"

    ```python
    class UserMutation(DjangoSerializerMutation):
        class Meta:
            serializer_class = UserSerializer

        @classmethod
        def save(cls, serialized_obj, root, info, **kwargs):
            # Custom validation before saving
            if serialized_obj.is_valid():
                # Additional business logic
                user = info.context.user
                if not user.has_perm('auth.add_user'):
                    raise PermissionError("Insufficient permissions")

                obj = serialized_obj.save()

                # Post-save operations
                send_welcome_email(obj.email)

                return True, obj
            else:
                errors = [
                    ErrorType(field=key, messages=value)
                    for key, value in serialized_obj.errors.items()
                ]
                return False, errors
    ```

### Schema Integration

=== "Individual Fields"

    ```python
    import graphene

    class Mutation(graphene.ObjectType):
        create_user = UserMutation.CreateField()
        update_user = UserMutation.UpdateField()
        delete_user = UserMutation.DeleteField()

    schema = graphene.Schema(query=Query, mutation=Mutation)
    ```

=== "All Fields at Once"

    ```python
    class Mutation(graphene.ObjectType):
        create_user, delete_user, update_user = UserMutation.MutationFields()

    schema = graphene.Schema(query=Query, mutation=Mutation)
    ```

### GraphQL Operations

#### Create Mutation

```graphql
mutation CreateUser($userData: UserInput!) {
  createUser(newUser: $userData) {
    ok
    user {
      id
      username
      email
    }
    errors {
      field
      messages
    }
  }
}
```

#### Update Mutation

```graphql
mutation UpdateUser($userData: UserInput!) {
  updateUser(newUser: $userData) {
    ok
    user {
      id
      username
      email
    }
    errors {
      field
      messages
    }
  }
}
```

#### Delete Mutation

```graphql
mutation DeleteUser($id: ID!) {
  deleteUser(id: $id) {
    ok
    user {
      id
      username
    }
    errors {
      field
      messages
    }
  }
}
```

### Response Structure

#### Success Response

```json
{
  "data": {
    "createUser": {
      "ok": true,
      "user": {
        "id": "1",
        "username": "john_doe",
        "email": "john@example.com"
      },
      "errors": null
    }
  }
}
```

#### Error Response

```json
{
  "data": {
    "createUser": {
      "ok": false,
      "user": null,
      "errors": [
        {
          "field": "username",
          "messages": ["This field is required."]
        },
        {
          "field": "email",
          "messages": ["Enter a valid email address."]
        }
      ]
    }
  }
}
```

## SerializerMutationOptions

Configuration options class for `DjangoSerializerMutation`.

```python
class SerializerMutationOptions(BaseOptions)
```

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `fields` | `dict` | GraphQL fields for the mutation |
| `input_fields` | `dict` | Input fields configuration |
| `interfaces` | `tuple` | GraphQL interfaces |
| `serializer_class` | `Serializer` | DRF serializer class |
| `action` | `str` | Mutation action type |
| `arguments` | `dict` | GraphQL arguments |
| `output` | `ObjectType` | Output type |
| `resolver` | `Callable` | Resolver function |
| `nested_fields` | `dict` | Nested field configuration |

## Advanced Usage

### File Upload Support

The mutation automatically handles file uploads when the request content type is `multipart/form-data`:

```python
class ProfileMutation(DjangoSerializerMutation):
    class Meta:
        serializer_class = ProfileSerializer  # Contains ImageField

# The mutation will automatically handle file uploads
```

```graphql
mutation UpdateProfile($profileData: ProfileInput!) {
  updateProfile(newProfile: $profileData) {
    ok
    profile {
      id
      avatar  # File upload handled automatically
      bio
    }
    errors {
      field
      messages
    }
  }
}
```

### Authentication & Authorization

```python
from graphql import GraphQLError

class UserMutation(DjangoSerializerMutation):
    class Meta:
        serializer_class = UserSerializer

    @classmethod
    def create(cls, root, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")

        if not user.has_perm('auth.add_user'):
            raise GraphQLError("Permission denied")

        return super().create(root, info, **kwargs)
```

### Custom Error Handling

```python
from django.core.exceptions import ValidationError

class UserMutation(DjangoSerializerMutation):
    class Meta:
        serializer_class = UserSerializer

    @classmethod
    def save(cls, serialized_obj, root, info, **kwargs):
        try:
            return super().save(serialized_obj, root, info, **kwargs)
        except ValidationError as e:
            errors = [
                ErrorType(field=field, messages=messages)
                for field, messages in e.message_dict.items()
            ]
            return False, errors
```

### Batch Operations

```python
import graphene

class BatchUserMutation(DjangoSerializerMutation):
    class Meta:
        serializer_class = UserSerializer

    class Arguments:
        users_data = graphene.List(graphene.String, required=True)

    @classmethod
    def create(cls, root, info, **kwargs):
        users_data = kwargs.get('users_data', [])
        created_users = []

        for user_data in users_data:
            serializer = cls._meta.serializer_class(data=user_data)
            if serializer.is_valid():
                user = serializer.save()
                created_users.append(user)
            else:
                return cls.get_errors([
                    ErrorType(field=f"user_{i}", messages=serializer.errors)
                    for i, user_data in enumerate(users_data)
                ])

        return cls.perform_mutate(created_users, info)
```

## Error Types

### ErrorType

Standard error type used in mutation responses.

```python
class ErrorType:
    field = graphene.String()
    messages = graphene.List(graphene.String)
```

## Best Practices

!!! tip "Mutation Best Practices"

    1. **Use DRF Serializers**: Leverage existing validation and business logic
    2. **Handle Permissions**: Always check authentication and authorization
    3. **Validate Input**: Use serializer validation for robust input handling
    4. **Return Meaningful Errors**: Provide clear, actionable error messages
    5. **Test Thoroughly**: Test all CRUD operations and edge cases
    6. **Document Operations**: Provide clear descriptions for mutations
    7. **Handle Files**: Use proper file upload handling for media fields

### Security Considerations

```python
class UserMutation(DjangoSerializerMutation):
    class Meta:
        serializer_class = UserSerializer
        # Don't expose sensitive operations
        exclude_fields = ('is_superuser', 'user_permissions', 'groups')

    @classmethod
    def get_serializer_kwargs(cls, root, info, **kwargs):
        return {
            'context': {
                'request': info.context,
                'user': info.context.user  # Pass current user for validation
            }
        }
```

### Performance Optimization

```python
class UserMutation(DjangoSerializerMutation):
    class Meta:
        serializer_class = UserSerializer

    @classmethod
    def save(cls, serialized_obj, root, info, **kwargs):
        if serialized_obj.is_valid():
            # Use bulk operations when possible
            with transaction.atomic():
                obj = serialized_obj.save()
                # Batch related operations
                return True, obj
        return super().save(serialized_obj, root, info, **kwargs)
```

This comprehensive API reference covers the mutation system in `graphene-django-extras`, providing developers with the tools needed to create robust, validated GraphQL mutations for their Django applications.
