# Utils API Reference

This section provides detailed API documentation for utility functions in `graphene-django-extras`.

## Model Utilities

### get_reverse_fields(model)

Get reverse relation fields from a Django model.

```python
def get_reverse_fields(model)
```

**Parameters:**
- `model` (`Model`): Django model class

**Returns:** Generator yielding tuples of `(field_name, field)`

**Example:**
```python
from django.contrib.auth.models import User
from graphene_django_extras.utils import get_reverse_fields

for name, field in get_reverse_fields(User):
    print(f"Reverse field: {name}")
```

### get_related_model(field)

Get the related model from a Django relation field.

```python
def get_related_model(field)
```

**Parameters:**
- `field` (`Field`): Django relation field

**Returns:** Related model class

**Example:**
```python
from myapp.models import Post
from graphene_django_extras.utils import get_related_model

author_field = Post._meta.get_field('author')
related_model = get_related_model(author_field)  # Returns User model
```

### get_model_fields(model)

Get all fields from a Django model including reverse fields.

```python
def get_model_fields(model)
```

**Parameters:**
- `model` (`Model`): Django model class

**Returns:** List of tuples `(field_name, field)`

**Example:**
```python
from graphene_django_extras.utils import get_model_fields

all_fields = get_model_fields(User)
for name, field in all_fields:
    print(f"Field: {name}, Type: {type(field)}")
```

### _resolve_model(obj)

Resolve supplied object to a Django model class.

```python
def _resolve_model(obj)
```

**Parameters:**
- `obj` (`str` or `Model`): Model class or string representation ('app_label.ModelName')

**Returns:** Django model class

**Raises:**
- `ImproperlyConfigured`: If model cannot be resolved
- `ValueError`: If obj is not a valid Django model reference

**Example:**
```python
from graphene_django_extras.utils import _resolve_model

# Using string reference
UserModel = _resolve_model('auth.User')

# Using model class
UserModel = _resolve_model(User)
```

---

## Object Management

### get_obj(app_label, model_name, object_id)

Get a Django object by app label, model name, and object ID.

```python
def get_obj(app_label, model_name, object_id)
```

**Parameters:**
- `app_label` (`str`): Django app label
- `model_name` (`str`): Model name
- `object_id` (`Any`): Object primary key

**Returns:** Model instance or `None`

**Raises:**
- `ValidationError`: If validation fails
- `TypeError`: If type conversion fails

**Example:**
```python
from graphene_django_extras.utils import get_obj

user = get_obj('auth', 'User', 1)
if user:
    print(f"Found user: {user.username}")
```

### create_obj(django_model, new_obj_key=None, *args, **kwargs)

Create a Django model instance with validation.

```python
def create_obj(django_model, new_obj_key=None, *args, **kwargs)
```

**Parameters:**
- `django_model` (`Model` or `str`): Django model class or string reference
- `new_obj_key` (`str`, optional): Key in kwargs containing the data
- `*args`: Additional positional arguments
- `**kwargs`: Model field values

**Returns:** Created model instance

**Raises:**
- `ValidationError`: If model validation fails
- `TypeError`: If type conversion fails

**Example:**
```python
from graphene_django_extras.utils import create_obj

# Direct field values
user = create_obj(User, username='john', email='john@example.com')

# Using nested data key
user_data = {'username': 'jane', 'email': 'jane@example.com'}
user = create_obj(User, new_obj_key='user_data', user_data=user_data)

# Using string model reference
user = create_obj('auth.User', username='bob', email='bob@example.com')
```

### get_Object_or_None(model, **kwargs)

Get an object or return None if it doesn't exist (safe get).

```python
def get_Object_or_None(model, **kwargs)
```

**Parameters:**
- `model` (`Model`): Django model class
- `**kwargs`: Lookup parameters

**Returns:** Model instance or `None`

**Example:**
```python
from graphene_django_extras.utils import get_Object_or_None

user = get_Object_or_None(User, username='john')
if user:
    print(f"User found: {user.email}")
else:
    print("User not found")
```

---

## String Utilities

### to_kebab_case(name)

Convert string to kebab-case format.

```python
def to_kebab_case(name)
```

**Parameters:**
- `name` (`str`): String to convert

**Returns:** String in kebab-case format

**Example:**
```python
from graphene_django_extras.utils import to_kebab_case

result = to_kebab_case("MyVariableName")  # "my-variable-name"
result = to_kebab_case("API Response")    # "api-response"
```

---

## Data Utilities

### clean_dict(d)

Remove all empty fields in a nested dictionary structure.

```python
def clean_dict(d)
```

**Parameters:**
- `d` (`dict` or `list`): Dictionary or list to clean

**Returns:** Cleaned dictionary/list with empty values removed

**Example:**
```python
from graphene_django_extras.utils import clean_dict

data = {
    'name': 'John',
    'email': '',
    'profile': {
        'bio': 'Developer',
        'avatar': None,
        'links': []
    },
    'tags': ['python', '', 'django']
}

cleaned = clean_dict(data)
# Result: {
#     'name': 'John',
#     'profile': {'bio': 'Developer'},
#     'tags': ['python', 'django']
# }
```

---

## GraphQL Utilities

### get_type(_type)

Get the base type from GraphQL type wrappers.

```python
def get_type(_type)
```

**Parameters:**
- `_type` (`GraphQLType`): GraphQL type (potentially wrapped)

**Returns:** Base GraphQL type

**Example:**
```python
from graphene import NonNull, List, String
from graphene_django_extras.utils import get_type

wrapped_type = NonNull(List(String))
base_type = get_type(wrapped_type)  # Returns String
```

### get_fields(info)

Extract field names from GraphQL query info.

```python
def get_fields(info)
```

**Parameters:**
- `info` (`ResolveInfo`): GraphQL resolve info object

**Returns:** Generator yielding field names

**Example:**
```python
from graphene_django_extras.utils import get_fields

def resolve_user(self, info, **kwargs):
    requested_fields = list(get_fields(info))
    print(f"Requested fields: {requested_fields}")
    
    # Optimize query based on requested fields
    queryset = User.objects.all()
    if 'profile' in requested_fields:
        queryset = queryset.select_related('profile')
    
    return queryset
```

### is_required(field)

Check if a Django field is required (not blank and no default).

```python
def is_required(field)
```

**Parameters:**
- `field` (`Field`): Django model field

**Returns:** `bool` - True if field is required

**Example:**
```python
from graphene_django_extras.utils import is_required

for field in User._meta.fields:
    if is_required(field):
        print(f"Required field: {field.name}")
```

---

## QuerySet Utilities

### _get_queryset(klass)

Return a QuerySet from a Model, Manager, or QuerySet.

```python
def _get_queryset(klass)
```

**Parameters:**
- `klass` (`Model`, `Manager`, or `QuerySet`): Object to convert to QuerySet

**Returns:** `QuerySet` instance

**Raises:**
- `ValueError`: If klass is not a valid type

**Example:**
```python
from graphene_django_extras.utils import _get_queryset

# From model class
qs = _get_queryset(User)

# From manager
qs = _get_queryset(User.objects)

# From existing queryset
active_users = User.objects.filter(is_active=True)
qs = _get_queryset(active_users)
```

### queryset_factory(manager, root, info, **kwargs)

Create optimized querysets based on GraphQL context.

```python
def queryset_factory(manager, root, info, **kwargs)
```

**Parameters:**
- `manager` (`Manager`): Django model manager
- `root` (`Any`): Root object in GraphQL resolution
- `info` (`ResolveInfo`): GraphQL resolve info
- `**kwargs`: Additional query parameters

**Returns:** Optimized `QuerySet`

**Example:**
```python
from graphene_django_extras.utils import queryset_factory

class UserType(DjangoObjectType):
    class Meta:
        model = User

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset_factory(
            User.objects, 
            None, 
            info,
            select_related=['profile'],
            prefetch_related=['posts']
        )
```

---

## Field Utilities

### find_field(field_node, available_fields)

Find a Django field based on GraphQL field node.

```python
def find_field(field_node, available_fields)
```

**Parameters:**
- `field_node` (`FieldNode`): GraphQL AST field node
- `available_fields` (`list`): List of available Django fields

**Returns:** Django field or `None`

### get_related_fields(model)

Get related fields from a Django model.

```python
def get_related_fields(model)
```

**Parameters:**
- `model` (`Model`): Django model class

**Returns:** Dictionary of related fields

**Example:**
```python
from graphene_django_extras.utils import get_related_fields

related_fields = get_related_fields(User)
for field_name, field in related_fields.items():
    print(f"Related field: {field_name}")
```

### get_extra_filters(root, model)

Get additional filters based on root object relationship.

```python
def get_extra_filters(root, model)
```

**Parameters:**
- `root` (`Any`): Root object
- `model` (`Model`): Target model class

**Returns:** Dictionary of filter parameters

---

## Validation Utilities

### validate_field_type(field, expected_type)

Validate that a Django field matches the expected type.

```python
def validate_field_type(field, expected_type)
```

**Parameters:**
- `field` (`Field`): Django model field
- `expected_type` (`type`): Expected field type

**Returns:** `bool` - True if field matches expected type

**Example:**
```python
from django.db import models
from graphene_django_extras.utils import validate_field_type

field = User._meta.get_field('email')
is_email_field = validate_field_type(field, models.EmailField)
```

---

## Error Handling Utilities

### safe_get_attr(obj, attr_path, default=None)

Safely get nested attributes from an object.

```python
def safe_get_attr(obj, attr_path, default=None)
```

**Parameters:**
- `obj` (`Any`): Object to get attribute from
- `attr_path` (`str`): Dot-separated attribute path (e.g., 'user.profile.bio')
- `default` (`Any`): Default value if attribute doesn't exist

**Returns:** Attribute value or default

**Example:**
```python
from graphene_django_extras.utils import safe_get_attr

# Safe access to nested attributes
bio = safe_get_attr(post, 'author.profile.bio', 'No bio available')
```

---

## Advanced Usage Examples

### Custom Field Resolution

```python
from graphene_django_extras.utils import get_fields, is_required

class CustomResolver:
    def resolve_users(self, info, **kwargs):
        # Get requested fields to optimize query
        requested_fields = list(get_fields(info))
        
        queryset = User.objects.all()
        
        # Optimize based on requested fields
        if 'profile' in requested_fields:
            queryset = queryset.select_related('profile')
        if 'posts' in requested_fields:
            queryset = queryset.prefetch_related('posts')
            
        return queryset
```

### Dynamic Model Creation

```python
from graphene_django_extras.utils import create_obj, get_obj

def create_user_with_profile(user_data, profile_data):
    try:
        # Create user
        user = create_obj(User, **user_data)
        
        # Create profile
        profile_data['user'] = user
        profile = create_obj('myapp.Profile', **profile_data)
        
        return user
    except ValidationError as e:
        print(f"Validation error: {e}")
        return None
```

### Field Analysis

```python
from graphene_django_extras.utils import get_model_fields, is_required

def analyze_model(model):
    """Analyze model fields and their requirements."""
    analysis = {
        'required_fields': [],
        'optional_fields': [],
        'relation_fields': []
    }
    
    for name, field in get_model_fields(model):
        if hasattr(field, 'related_model'):
            analysis['relation_fields'].append(name)
        elif is_required(field):
            analysis['required_fields'].append(name)
        else:
            analysis['optional_fields'].append(name)
    
    return analysis

# Usage
user_analysis = analyze_model(User)
print(f"Required fields: {user_analysis['required_fields']}")
```

## Best Practices

!!! tip "Utils Best Practices"

    1. **Error Handling**: Always handle exceptions when using object creation utilities
    2. **Performance**: Use queryset optimization utilities for better database performance
    3. **Validation**: Utilize field validation utilities before processing data
    4. **Type Safety**: Use type checking utilities to ensure data consistency
    5. **Caching**: Cache results of expensive utility operations when appropriate

### Performance Optimization

```python
from graphene_django_extras.utils import queryset_factory, get_fields

class OptimizedQuery:
    def resolve_posts(self, info, **kwargs):
        # Use queryset factory for optimization
        base_qs = queryset_factory(Post.objects, None, info)
        
        # Further optimize based on requested fields
        requested_fields = list(get_fields(info))
        
        if any(field.startswith('author') for field in requested_fields):
            base_qs = base_qs.select_related('author')
        
        if 'comments' in requested_fields:
            base_qs = base_qs.prefetch_related('comments')
            
        return base_qs
```

### Error Handling

```python
from graphene_django_extras.utils import get_obj, create_obj
from django.core.exceptions import ValidationError

def safe_create_user(user_data):
    try:
        return create_obj(User, **user_data)
    except ValidationError as e:
        logger.error(f"User creation failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None
```

This comprehensive API reference covers all utility functions in `graphene-django-extras`, providing developers with powerful tools for Django-GraphQL integration and optimization.