# Directives API Reference

This section provides detailed API documentation for GraphQL directives in `graphene-django-extras`.

## BaseExtraGraphQLDirective

Abstract base class for all custom GraphQL directives.

```python
class BaseExtraGraphQLDirective(GraphQLDirective)
```

### Methods

#### `get_args()` (staticmethod)

Define the arguments that the directive accepts.

**Returns:** `dict` of GraphQL arguments

**Example:**
```python
@staticmethod
def get_args():
    return {
        "format": GraphQLArgument(
            GraphQLString,
            description="Format string"
        )
    }
```

#### `resolve(value, directive, root, info, **kwargs)` (staticmethod)

Process the field value with the directive.

**Parameters:**
- `value` (`Any`): The field value to transform
- `directive` (`DirectiveNode`): GraphQL directive AST node
- `root` (`Any`): Root object
- `info` (`ResolveInfo`): GraphQL resolve info
- `**kwargs`: Additional keyword arguments

**Returns:** Transformed value

---

## String Directives

### DefaultGraphQLDirective

Provides default values for null or empty strings.

```python
@default(to: "fallback value")
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `to` | `String!` | Yes | Value to use as default |

#### Example

```graphql
query {
  user {
    bio @default(to: "No bio available")
  }
}
```

### Base64GraphQLDirective

Encode or decode strings using base64.

```python
@base64(op: "encode")
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `op` | `String` | No | Operation: "encode" or "decode" |

#### Example

```graphql
query {
  apiKey @base64(op: "encode")
  token @base64(op: "decode")
}
```

### Case Conversion Directives

#### LowercaseGraphQLDirective

Convert string to lowercase.

```python
@lowercase
```

#### UppercaseGraphQLDirective

Convert string to uppercase.

```python
@uppercase
```

#### CapitalizeGraphQLDirective

Capitalize first character, lowercase the rest.

```python
@capitalize
```

#### TitleCaseGraphQLDirective

Convert to title case (first letter of each word capitalized).

```python
@titleCase
```

#### SwapCaseGraphQLDirective

Swap case of all characters.

```python
@swapCase
```

#### Example

```graphql
query {
  user {
    name @uppercase
    email @lowercase
    title @titleCase
    status @capitalize
  }
}
```

### Code Style Directives

#### CamelCaseGraphQLDirective

Convert string to camelCase.

```python
@camelCase
```

#### SnakeCaseGraphQLDirective

Convert string to snake_case.

```python
@snakeCase
```

#### KebabCaseGraphQLDirective

Convert string to kebab-case.

```python
@kebabCase
```

#### Example

```graphql
query {
  field {
    displayName @camelCase  # "myDisplayName"
    apiName @snakeCase      # "my_api_name"
    urlSlug @kebabCase      # "my-url-slug"
  }
}
```

### String Manipulation Directives

#### StripGraphQLDirective

Remove leading and trailing characters.

```python
@strip(chars: " ")
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `chars` | `String` | No | Characters to strip (default: whitespace) |

#### CenterGraphQLDirective

Center string within a specified width.

```python
@center(width: 20, fillchar: "-")
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `width` | `Int!` | Yes | Total width of result string |
| `fillchar` | `String` | No | Character to use for padding (default: space) |

#### ReplaceGraphQLDirective

Replace occurrences of a substring.

```python
@replace(old: "GraphQL", new: "GQL", count: 1)
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `old` | `String!` | Yes | Substring to replace |
| `new` | `String!` | Yes | Replacement string |
| `count` | `Int` | No | Max number of replacements (-1 for all) |

#### Example

```graphql
query {
  post {
    content @strip
    title @center(width: 50, fillchar: "=")
    text @replace(old: "API", new: "Application Programming Interface")
  }
}
```

---

## Number Directives

### NumberGraphQLDirective

Format numbers using Python format strings.

```python
@number(as: ".2f")
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `as` | `String!` | Yes | Python format string |

#### Example

```graphql
query {
  product {
    price @number(as: ".2f")      # "123.45"
    weight @number(as: ".3f")     # "12.500"
    rating @number(as: ".1%")     # "45.2%"
  }
}
```

### CurrencyGraphQLDirective

Format numbers as currency.

```python
@currency(symbol: "$")
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `symbol` | `String` | No | Currency symbol (default: "$") |

#### Example

```graphql
query {
  product {
    priceUSD @currency             # "$123.45"
    priceEUR @currency(symbol: "€") # "€123.45"
    priceGBP @currency(symbol: "£") # "£123.45"
  }
}
```

### Mathematical Directives

#### FloorGraphQLDirective

Return the floor of a number.

```python
@floor
```

#### CeilGraphQLDirective

Return the ceiling of a number.

```python
@ceil
```

#### Example

```graphql
query {
  stats {
    averageRating @floor  # 4.7 → 4
    priceEstimate @ceil   # 99.1 → 100
  }
}
```

---

## Date Directives

### DateGraphQLDirective

Format dates and times using various formats.

```python
@date(format: "YYYY-MM-DD")
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `format` | `String` | No | Date format string (default: "default") |

#### Format Options

##### Predefined Formats

| Format | Description | Example |
|--------|-------------|---------|
| `"default"` | Standard format | "01 Dec 2023 14:30:00" |
| `"iso"` | ISO format | "2023-Dec-01T14:30:00" |
| `"javascript"` | JS Date format | "Fri Dec 01 2023 14:30:00" |
| `"time ago"` | Relative time | "2 hours ago" |
| `"time ago 2d"` | Relative with fallback | "Yesterday" or "Dec 01, 2023" |

##### Custom Format Tokens

| Token | Description | Example |
|-------|-------------|---------|
| `YYYY` | 4-digit year | 2023 |
| `YY` | 2-digit year | 23 |
| `MMMM` | Full month name | December |
| `MMM` | Short month name | Dec |
| `MM` | Month number (padded) | 12 |
| `DD` | Day of month (padded) | 01 |
| `dddd` | Full day name | Friday |
| `ddd` | Short day name | Fri |
| `HH` | Hour (24h, padded) | 14 |
| `hh` | Hour (12h, padded) | 02 |
| `mm` | Minutes (padded) | 30 |
| `ss` | Seconds (padded) | 45 |
| `A` | AM/PM | PM |

#### Example

```graphql
query {
  post {
    createdAt @date(format: "YYYY-MM-DD")         # "2023-12-01"
    updatedAt @date(format: "MMMM DD, YYYY")      # "December 01, 2023"
    publishedAt @date(format: "time ago")         # "2 hours ago"
    timestamp @date(format: "DD/MM/YY HH:mm A")   # "01/12/23 02:30 PM"
  }
}
```

---

## List Directives

### ShuffleGraphQLDirective

Randomly reorder list elements.

```python
@shuffle
```

#### Example

```graphql
query {
  post {
    tags @shuffle {
      name
      color
    }
  }
}
```

### SampleGraphQLDirective

Get a random sample from a list.

```python
@sample(size: 3)
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `size` | `Int` | No | Number of items to sample |

#### Example

```graphql
query {
  post {
    tags @sample(size: 3) {  # Get 3 random tags
      name
      color
    }
  }
}
```

---

## Middleware Integration

### ExtraGraphQLDirectiveMiddleware

Middleware class that processes directives during query execution.

```python
class ExtraGraphQLDirectiveMiddleware:
    def resolve(self, next, root, info, **args):
        # Process directives on field resolution
        pass
```

#### Django Settings

```python
GRAPHENE = {
    'SCHEMA': 'myapp.schema.schema',
    'MIDDLEWARE': [
        'graphene_django_extras.ExtraGraphQLDirectiveMiddleware',
    ],
}
```

---

## Custom Directives

### Creating Custom Directives

```python
from graphene_django_extras.directives.base import BaseExtraGraphQLDirective
from graphql import GraphQLArgument, GraphQLString, GraphQLInt

class TruncateGraphQLDirective(BaseExtraGraphQLDirective):
    """Truncate string to specified length."""

    @staticmethod
    def get_args():
        return {
            "length": GraphQLArgument(
                GraphQLInt,
                description="Maximum length of string"
            ),
            "suffix": GraphQLArgument(
                GraphQLString,
                description="Suffix to add when truncated"
            )
        }

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        # Extract arguments
        length_arg = next(
            (arg for arg in directive.arguments if arg.name.value == "length"),
            None
        )
        suffix_arg = next(
            (arg for arg in directive.arguments if arg.name.value == "suffix"),
            None
        )

        length = int(length_arg.value.value) if length_arg else 100
        suffix = suffix_arg.value.value if suffix_arg else "..."

        # Process value
        str_value = str(value)
        if len(str_value) <= length:
            return str_value

        return str_value[:length - len(suffix)] + suffix
```

### Registering Custom Directives

```python
import graphene
from graphene_django_extras import all_directives

# Add custom directive to the list
custom_directives = [
    *all_directives,
    TruncateGraphQLDirective()
]

schema = graphene.Schema(
    query=Query,
    directives=custom_directives
)
```

### Using Custom Directives

```graphql
query {
  post {
    content @truncate(length: 100, suffix: "...")
    title @truncate(length: 50)
  }
}
```

---

## Directive Utilities

### Argument Extraction Helper

```python
def get_directive_arg(directive, arg_name, default=None):
    """Extract argument value from directive."""
    arg = next(
        (arg for arg in directive.arguments if arg.name.value == arg_name),
        None
    )
    return arg.value.value if arg else default
```

### Type Checking Helper

```python
def ensure_string(value):
    """Ensure value is a string."""
    if isinstance(value, six.string_types):
        return value
    return str(value) if value is not None else ""
```

---

## Error Handling

### Graceful Degradation

```python
class SafeDirective(BaseExtraGraphQLDirective):
    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        try:
            # Directive processing logic
            return process_value(value)
        except Exception as e:
            # Log error and return original value
            logger.warning(f"Directive processing failed: {e}")
            return value
```

### Validation

```python
class ValidatedDirective(BaseExtraGraphQLDirective):
    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        if value is None:
            return None

        if not isinstance(value, (str, int, float)):
            raise ValueError("Directive only accepts string/number values")

        return process_value(value)
```

---

## Performance Considerations

### Caching Directive Results

```python
from django.core.cache import cache

class CachedDirective(BaseExtraGraphQLDirective):
    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        cache_key = f"directive_{hash(str(value))}"
        cached_result = cache.get(cache_key)

        if cached_result is not None:
            return cached_result

        result = expensive_processing(value)
        cache.set(cache_key, result, 300)  # 5 minutes
        return result
```

### Directive Ordering

```python
# Directives are processed in the order they appear
query {
  field @strip @uppercase @truncate(length: 50)
  # 1. Strip whitespace
  # 2. Convert to uppercase
  # 3. Truncate to 50 characters
}
```

---

## Best Practices

!!! tip "Directive Best Practices"

    1. **Handle Null Values**: Always check for null/undefined values
    2. **Provide Defaults**: Use sensible defaults for optional arguments
    3. **Validate Input**: Validate argument types and values
    4. **Error Gracefully**: Return original value on processing errors
    5. **Document Arguments**: Provide clear descriptions for all arguments
    6. **Consider Performance**: Cache expensive operations when possible
    7. **Test Thoroughly**: Test with various input types and edge cases

### Security Considerations

```python
class SecureDirective(BaseExtraGraphQLDirective):
    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        # Validate permissions
        user = info.context.user
        if not user.is_authenticated:
            return value  # Don't process for unauthenticated users

        # Sanitize input
        safe_value = escape_html(str(value))

        return process_value(safe_value)
```

### Testing Directives

```python
import pytest
from graphene.test import Client

def test_uppercase_directive():
    schema = graphene.Schema(
        query=Query,
        directives=all_directives
    )
    client = Client(schema)

    query = '''
        query {
            user {
                name @uppercase
            }
        }
    '''

    result = client.execute(query)
    assert result['data']['user']['name'] == 'JOHN DOE'
```

This comprehensive API reference covers all directive classes and utilities in `graphene-django-extras`, providing developers with the knowledge needed to use and create custom GraphQL directives for their applications.
