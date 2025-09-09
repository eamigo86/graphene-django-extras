# Mutations

GraphQL mutations allow you to modify data on your server. `graphene-django-extras` provides powerful tools to create mutations based on Django serializers, making CRUD operations simple and consistent.

## DjangoSerializerMutation

The `DjangoSerializerMutation` is the cornerstone of mutations in `graphene-django-extras`. It automatically generates Create, Read, Update, and Delete (CRUD) operations based on your Django REST Framework serializers.

### Features

- :material-auto-fix: **Automatic CRUD Operations**: Generates create, update, and delete mutations
- :material-check-circle: **Built-in Validation**: Uses Django REST Framework serializer validation
- :material-file-upload: **File Upload Support**: Handles multipart/form-data requests
- :material-link-variant: **Nested Relationships**: Supports nested field creation and updates
- :material-alert-circle: **Error Handling**: Returns structured error responses

### Basic Usage

=== "Define Your Mutation"

    ```python
    from graphene_django_extras import DjangoSerializerMutation
    from .serializers import UserSerializer

    class UserMutation(DjangoSerializerMutation):
        class Meta:
            serializer_class = UserSerializer
            description = "User mutations: create, update, delete"
    ```

=== "Add to Schema"

    ```python
    import graphene
    from .mutations import UserMutation

    class Mutation(graphene.ObjectType):
        # Get all mutation fields (create, update, delete)
        user_create, user_delete, user_update = UserMutation.MutationFields()

    schema = graphene.Schema(query=Query, mutation=Mutation)
    ```

=== "Alternative Schema Setup"

    ```python
    import graphene
    from .mutations import UserMutation

    class Mutation(graphene.ObjectType):
        # Individual mutation fields
        create_user = UserMutation.CreateField()
        update_user = UserMutation.UpdateField()
        delete_user = UserMutation.DeleteField()

    schema = graphene.Schema(query=Query, mutation=Mutation)
    ```

### Configuration Options

The `DjangoSerializerMutation` supports several configuration options:

#### Meta Configuration

```python
class UserMutation(DjangoSerializerMutation):
    class Meta:
        serializer_class = UserSerializer
        only_fields = ('username', 'email', 'first_name', 'last_name')
        exclude_fields = ('password',)
        input_field_name = 'user_data'  # Default: 'new_{model_name}'
        output_field_name = 'user'      # Default: '{model_name}'
        description = "Custom description for the mutation"
        nested_fields = {
            'profile': ProfileSerializer,
            'addresses': AddressSerializer
        }
```

#### Field Filtering

!!! tip "Field Control"
    Use `only_fields` to include specific fields, or `exclude_fields` to exclude certain fields from mutations.

=== "Include Specific Fields"

    ```python
    class UserMutation(DjangoSerializerMutation):
        class Meta:
            serializer_class = UserSerializer
            only_fields = ('username', 'email', 'first_name', 'last_name')
    ```

=== "Exclude Fields"

    ```python
    class UserMutation(DjangoSerializerMutation):
        class Meta:
            serializer_class = UserSerializer
            exclude_fields = ('password', 'is_staff', 'is_superuser')
    ```

### Custom Arguments

You can add custom arguments to your mutations:

```python
class UserMutation(DjangoSerializerMutation):
    class Meta:
        serializer_class = UserSerializer

    class Arguments:
        send_email = graphene.Boolean(
            default_value=False,
            description="Send welcome email after user creation"
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

### Nested Fields Support

Handle related models with nested fields:

```python
class UserMutation(DjangoSerializerMutation):
    class Meta:
        serializer_class = UserSerializer
        nested_fields = {
            'profile': ProfileSerializer,        # One-to-one relationship
            'addresses': AddressSerializer       # Many-to-many relationship
        }
```

!!! info "Nested Fields Behavior"
    - For single objects: The created object's ID is assigned to the field
    - For lists: Objects are added to the many-to-many relationship

### File Upload Support

The mutation automatically handles file uploads when the request content type is `multipart/form-data`:

```python
# Your serializer
class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField()
    
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']

# The mutation will automatically handle avatar uploads
class ProfileMutation(DjangoSerializerMutation):
    class Meta:
        serializer_class = ProfileSerializer
```

### Error Handling

All mutations return a consistent response structure:

```python
{
  "ok": Boolean,           # True if successful, False if errors
  "errors": [ErrorType],   # List of validation errors
  "{model_name}": Object   # The created/updated/deleted object (null if errors)
}
```

Example error response:

```json
{
  "data": {
    "createUser": {
      "ok": false,
      "errors": [
        {
          "field": "email",
          "messages": ["This field is required."]
        },
        {
          "field": "username", 
          "messages": ["A user with that username already exists."]
        }
      ],
      "user": null
    }
  }
}
```

### Custom Mutation Logic

Override methods to add custom logic:

=== "Custom Validation"

    ```python
    class UserMutation(DjangoSerializerMutation):
        class Meta:
            serializer_class = UserSerializer

        @classmethod
        def get_serializer_kwargs(cls, root, info, **kwargs):
            return {
                'context': {
                    'request': info.context,
                    'user': info.context.user
                }
            }
    ```

=== "Custom Save Logic"

    ```python
    class UserMutation(DjangoSerializerMutation):
        class Meta:
            serializer_class = UserSerializer

        @classmethod
        def save(cls, serialized_obj, root, info, **kwargs):
            if serialized_obj.is_valid():
                # Custom logic before saving
                obj = serialized_obj.save()
                
                # Custom logic after saving
                send_welcome_email(obj.email)
                
                return True, obj
            else:
                errors = [
                    ErrorType(field=key, messages=value)
                    for key, value in serialized_obj.errors.items()
                ]
                return False, errors
    ```

### Complete Example

Here's a complete example showing all features:

=== "models.py"

    ```python
    from django.db import models
    from django.contrib.auth.models import User

    class Profile(models.Model):
        user = models.OneToOneField(User, on_delete=models.CASCADE)
        bio = models.TextField(blank=True)
        avatar = models.ImageField(upload_to='avatars/', blank=True)
        birth_date = models.DateField(null=True, blank=True)

    class Address(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE)
        street = models.CharField(max_length=255)
        city = models.CharField(max_length=100)
        country = models.CharField(max_length=100)
    ```

=== "serializers.py"

    ```python
    from rest_framework import serializers
    from django.contrib.auth.models import User
    from .models import Profile, Address

    class ProfileSerializer(serializers.ModelSerializer):
        class Meta:
            model = Profile
            fields = ['bio', 'avatar', 'birth_date']

    class AddressSerializer(serializers.ModelSerializer):
        class Meta:
            model = Address
            fields = ['street', 'city', 'country']

    class UserSerializer(serializers.ModelSerializer):
        password = serializers.CharField(write_only=True)
        
        class Meta:
            model = User
            fields = ['username', 'email', 'first_name', 'last_name', 'password']

        def create(self, validated_data):
            password = validated_data.pop('password')
            user = User.objects.create(**validated_data)
            user.set_password(password)
            user.save()
            return user
    ```

=== "mutations.py"

    ```python
    from graphene_django_extras import DjangoSerializerMutation
    from .serializers import UserSerializer, ProfileSerializer, AddressSerializer

    class UserMutation(DjangoSerializerMutation):
        class Meta:
            serializer_class = UserSerializer
            exclude_fields = ('is_staff', 'is_superuser')
            nested_fields = {
                'profile': ProfileSerializer,
                'addresses': AddressSerializer
            }

        class Arguments:
            send_welcome_email = graphene.Boolean(default_value=True)

        @classmethod
        def get_serializer_kwargs(cls, root, info, **kwargs):
            return {
                'context': {
                    'request': info.context,
                    'send_welcome': kwargs.get('send_welcome_email', True)
                }
            }
    ```

=== "schema.py"

    ```python
    import graphene
    from .mutations import UserMutation

    class Mutation(graphene.ObjectType):
        create_user, delete_user, update_user = UserMutation.MutationFields()

    schema = graphene.Schema(query=Query, mutation=Mutation)
    ```

## Traditional GraphQL Mutations

While `DjangoSerializerMutation` covers most use cases, you can still create traditional GraphQL mutations for custom logic:

=== "Traditional Mutation"

    ```python
    import graphene
    from graphene_django.types import DjangoObjectType
    from django.contrib.auth.models import User

    class UserType(DjangoObjectType):
        class Meta:
            model = User

    class CreateUser(graphene.Mutation):
        class Arguments:
            username = graphene.String(required=True)
            email = graphene.String(required=True)
            password = graphene.String(required=True)

        ok = graphene.Boolean()
        user = graphene.Field(UserType)

        def mutate(self, info, username, email, password):
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            return CreateUser(ok=True, user=user)
    ```

=== "With Error Handling"

    ```python
    from graphene_django.types import ErrorType

    class CreateUser(graphene.Mutation):
        class Arguments:
            username = graphene.String(required=True)
            email = graphene.String(required=True)
            password = graphene.String(required=True)

        ok = graphene.Boolean()
        user = graphene.Field(UserType)
        errors = graphene.List(ErrorType)

        def mutate(self, info, username, email, password):
            # Validation
            errors = []
            
            if User.objects.filter(username=username).exists():
                errors.append(ErrorType(
                    field="username",
                    messages=["Username already exists"]
                ))
            
            if User.objects.filter(email=email).exists():
                errors.append(ErrorType(
                    field="email", 
                    messages=["Email already registered"]
                ))
                
            if errors:
                return CreateUser(ok=False, errors=errors, user=None)
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            return CreateUser(ok=True, user=user, errors=None)
    ```

## Best Practices

!!! tip "Mutation Best Practices"

    1. **Use DjangoSerializerMutation**: Leverage existing serializers for consistency
    2. **Validate Input**: Always validate input data before processing
    3. **Handle Errors Gracefully**: Provide clear, actionable error messages
    4. **Test Thoroughly**: Write tests for all mutation scenarios
    5. **Document Fields**: Use descriptions for all mutation fields and arguments
    6. **Security First**: Implement proper authentication and authorization

### Authentication & Permissions

```python
from graphql import GraphQLError

class UserMutation(DjangoSerializerMutation):
    class Meta:
        serializer_class = UserSerializer

    @classmethod
    def create(cls, root, info, **kwargs):
        if not info.context.user.is_authenticated:
            raise GraphQLError("Authentication required")
            
        if not info.context.user.has_perm('auth.add_user'):
            raise GraphQLError("Permission denied")
            
        return super().create(root, info, **kwargs)
```

### Input Validation

```python
class UserMutation(DjangoSerializerMutation):
    class Meta:
        serializer_class = UserSerializer

    @classmethod
    def get_serializer_kwargs(cls, root, info, **kwargs):
        # Add custom validation context
        return {
            'context': {
                'request': info.context,
                'current_user': info.context.user
            }
        }
```

## Testing Mutations

=== "Basic Test"

    ```python
    import pytest
    from graphene.test import Client
    from .schema import schema

    @pytest.mark.django_db
    def test_create_user_mutation():
        client = Client(schema)
        
        mutation = """
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
        """
        
        variables = {
            "userData": {
                "username": "testuser",
                "email": "test@example.com",
                "password": "secretpass123"
            }
        }
        
        result = client.execute(mutation, variables=variables)
        assert result['data']['createUser']['ok'] is True
        assert result['data']['createUser']['user']['username'] == 'testuser'
    ```

=== "Error Handling Test"

    ```python
    @pytest.mark.django_db
    def test_create_user_validation_error():
        client = Client(schema)
        
        mutation = """
            mutation CreateUser($userData: UserInput!) {
                createUser(newUser: $userData) {
                    ok
                    errors {
                        field
                        messages
                    }
                }
            }
        """
        
        # Missing required email
        variables = {
            "userData": {
                "username": "testuser",
                "password": "secretpass123"
            }
        }
        
        result = client.execute(mutation, variables=variables)
        assert result['data']['createUser']['ok'] is False
        assert len(result['data']['createUser']['errors']) > 0
    ```

The mutation system in `graphene-django-extras` provides a robust foundation for handling data modifications in your GraphQL API, with built-in validation, error handling, and support for complex operations.