# GraphQL Directives

GraphQL directives in `graphene-django-extras` allow you to transform field values at query execution time. They provide a powerful way to format, manipulate, and transform data without modifying your underlying models or resolvers.

## Overview

Directives are applied to fields in your GraphQL queries and are processed after the field value is resolved. They enable you to:

- :material-format-text: **Format strings**: Transform text case, encoding, and structure
- :material-calendar: **Format dates**: Display dates in various formats and relative time
- :material-calculator: **Format numbers**: Apply number formatting and currency display
- :material-shuffle-variant: **Manipulate lists**: Transform and sample list data

## Usage

Directives are applied in GraphQL queries using the `@directive_name` syntax:

```graphql
query {
  user {
    name @uppercase
    email @lowercase
    joinDate @date(format: "MMMM DD, YYYY")
    balance @currency(symbol: "€")
  }
}
```

## String Directives

String directives provide various text transformation capabilities:

### Case Conversion

Transform text case with these directives:

=== "Uppercase & Lowercase"

    ```graphql
    query GetUser {
      user {
        name @uppercase        # "JOHN DOE"
        email @lowercase       # "john.doe@example.com"
        bio @capitalize        # "Hello world" → "Hello world"
        title @titleCase       # "hello world" → "Hello World"
        status @swapCase       # "Hello" → "hELLO"
      }
    }
    ```

=== "Code Style Conversion"

    ```graphql
    query GetData {
      post {
        title @camelCase       # "My Blog Post" → "myBlogPost"
        slug @snakeCase        # "My Blog Post" → "my_blog_post"
        url @kebabCase         # "My Blog Post" → "my-blog-post"
      }
    }
    ```

### String Manipulation

=== "Trimming and Padding"

    ```graphql
    query GetContent {
      post {
        content @strip                    # Remove whitespace
        title @strip(chars: ".")          # Remove specific characters
        code @center(width: 20)           # Center text in 20 characters
        header @center(width: 30, fillchar: "-")  # Center with dashes
      }
    }
    ```

=== "Find and Replace"

    ```graphql
    query GetPost {
      post {
        content @replace(old: "GraphQL", new: "GQL")
        text @replace(old: " ", new: "_", count: 3)  # Replace first 3 spaces
      }
    }
    ```

### Default Values

Provide fallback values for empty or null fields:

=== "Default Directive"

    ```graphql
    query GetUser {
      user {
        firstName @default(to: "Anonymous")
        lastName @default(to: "User")
        bio @default(to: "No bio available")
      }
    }
    ```

=== "Example Response"

    ```json
    {
      "data": {
        "user": {
          "firstName": "John",        // Original value
          "lastName": "Anonymous",    // Default applied (was null)
          "bio": "No bio available"  // Default applied (was empty)
        }
      }
    }
    ```

### Encoding Directives

Handle base64 encoding and decoding:

=== "Base64 Operations"

    ```graphql
    query GetData {
      apiKey @base64(op: "encode")      # Encode to base64
      token @base64(op: "decode")       # Decode from base64
    }
    ```

=== "Example"

    ```json
    // Input: "hello world"
    // With @base64(op: "encode"): "aGVsbG8gd29ybGQ="
    // With @base64(op: "decode"): Original string from base64
    ```

## Number Directives

Format numeric values with precision and style:

### Basic Number Formatting

=== "Number Directive"

    ```graphql
    query GetStats {
      product {
        price @number(as: ".2f")        # "123.45"
        weight @number(as: ".3f")       # "12.500"
        rating @number(as: ".1f")       # "4.2"
      }
    }
    ```

### Currency Formatting

Format numbers as currency with customizable symbols:

=== "Currency Examples"

    ```graphql
    query GetPrices {
      product {
        priceUSD @currency                    # "$123.45" (default)
        priceEUR @currency(symbol: "€")       # "€123.45"
        priceGBP @currency(symbol: "£")       # "£123.45"
        priceJPY @currency(symbol: "¥")       # "¥123.45"
      }
    }
    ```

=== "Response Example"

    ```json
    {
      "data": {
        "product": {
          "priceUSD": "$1,234.56",
          "priceEUR": "€1,234.56",
          "priceGBP": "£1,234.56",
          "priceJPY": "¥1,234.56"
        }
      }
    }
    ```

## Date Directives

Powerful date and time formatting with multiple options:

### Standard Date Formats

=== "Common Formats"

    ```graphql
    query GetPost {
      post {
        createdAt @date(format: "YYYY-MM-DD")         # "2023-12-01"
        updatedAt @date(format: "MMMM DD, YYYY")      # "December 01, 2023"
        publishedAt @date(format: "DD/MM/YYYY HH:mm") # "01/12/2023 14:30"
        timestamp @date(format: "iso")                # "2023-Dec-01T14:30:00"
        jsDate @date(format: "javascript")            # "Fri Dec 01 2023 14:30:00"
      }
    }
    ```

### Relative Time Formatting

=== "Time Ago Formats"

    ```graphql
    query GetActivity {
      post {
        createdAt @date(format: "time ago")       # "2 hours ago" / "in 3 days"
        updatedAt @date(format: "time ago 2d")    # Shows "Yesterday", "Tomorrow", or date
      }
    }
    ```

=== "Relative Time Examples"

    ```json
    {
      "data": {
        "post": {
          "createdAt": "2 hours ago",
          "updatedAt": "Yesterday"    // or "Dec 01, 2023" if more than 2 days
        }
      }
    }
    ```

### Custom Date Patterns

Build custom date formats using these tokens:

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

=== "Custom Format Examples"

    ```graphql
    query GetEvents {
      event {
        startDate @date(format: "dddd, MMMM DD, YYYY")    # "Friday, December 01, 2023"
        endDate @date(format: "DD-MM-YY HH:mm A")         # "01-12-23 02:30 PM"
        created @date(format: "YYYY/MM/DD")               # "2023/12/01"
      }
    }
    ```

## List Directives

Transform and manipulate list data:

### Shuffle Directive

Randomly reorder list elements:

=== "Shuffle Lists"

    ```graphql
    query GetRandomPosts {
      posts {
        tags @shuffle {
          name
          color
        }
      }
    }
    ```

### Sample Directive

Get a random sample from a list:

=== "Sample Lists"

    ```graphql
    query GetSampleTags {
      post {
        tags @sample(size: 3) {  # Get 3 random tags
          name
          color
        }
      }
    }
    ```

## Math Directives

Perform mathematical operations on numbers:

### Floor and Ceil

=== "Rounding Operations"

    ```graphql
    query GetStats {
      product {
        rating @floor      # 4.7 → 4
        price @ceil        # 99.1 → 100
      }
    }
    ```

## Combining Directives

Chain multiple directives for complex transformations:

=== "Directive Chaining"

    ```graphql
    query GetFormattedData {
      user {
        firstName @default(to: "Anonymous") @titleCase @strip
        email @lowercase @strip
        bio @default(to: "No bio") @capitalize @replace(old: ".", new: "!")
      }
      post {
        title @titleCase @replace(old: "GraphQL", new: "GQL")
        viewCount @number(as: ",.0f")
        createdAt @date(format: "MMMM DD, YYYY")
      }
    }
    ```

=== "Example Response"

    ```json
    {
      "data": {
        "user": {
          "firstName": "Anonymous",
          "email": "user@example.com",
          "bio": "Welcome to my profile!"
        },
        "post": {
          "title": "Getting Started With GQL",
          "viewCount": "1,245",
          "createdAt": "December 01, 2023"
        }
      }
    }
    ```

## Custom Directives

While `graphene-django-extras` provides many built-in directives, you can create custom ones:

=== "Custom Directive Example"

    ```python
    from graphene_django_extras.directives.base import BaseExtraGraphQLDirective
    from graphql import GraphQLArgument, GraphQLString

    class TruncateGraphQLDirective(BaseExtraGraphQLDirective):
        """Truncate string to specified length."""

        @staticmethod
        def get_args():
            return {
                "length": GraphQLArgument(
                    GraphQLString,
                    description="Maximum length of string"
                ),
                "suffix": GraphQLArgument(
                    GraphQLString,
                    description="Suffix to add when truncated (default: '...')"
                )
            }

        @staticmethod
        def resolve(value, directive, root, info, **kwargs):
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

            if len(str(value)) <= length:
                return value

            return str(value)[:length - len(suffix)] + suffix
    ```

## Schema Integration

Add directives to your GraphQL schema:

=== "Schema Setup"

    ```python
    import graphene
    from graphene_django_extras import all_directives

    class Query(graphene.ObjectType):
        # Your query fields here
        pass

    schema = graphene.Schema(
        query=Query,
        directives=all_directives  # Include all built-in directives
    )
    ```

=== "Custom Directives"

    ```python
    from graphene_django_extras import all_directives
    from .directives import TruncateGraphQLDirective

    custom_directives = [
        *all_directives,
        TruncateGraphQLDirective()
    ]

    schema = graphene.Schema(
        query=Query,
        directives=custom_directives
    )
    ```

## Middleware Integration

Enable directive processing with middleware:

=== "Django Settings"

    ```python
    GRAPHENE = {
        'SCHEMA': 'myapp.schema.schema',
        'MIDDLEWARE': [
            'graphene_django_extras.ExtraGraphQLDirectiveMiddleware',
        ],
    }
    ```

## Real-World Examples

### Blog Post Formatting

=== "Blog Query"

    ```graphql
    query GetBlogPost {
      post(id: "1") {
        title @titleCase
        content @strip
        excerpt @default(to: "No excerpt available") @capitalize
        author {
          name @titleCase
          email @lowercase
          bio @default(to: "No bio") @strip
        }
        publishedAt @date(format: "MMMM DD, YYYY")
        updatedAt @date(format: "time ago")
        viewCount @number(as: ",.0f")
        tags @sample(size: 5) {
          name @uppercase
        }
      }
    }
    ```

### E-commerce Product Display

=== "Product Query"

    ```graphql
    query GetProduct {
      product(id: "123") {
        name @titleCase
        description @strip @default(to: "No description available")
        price @currency(symbol: "$")
        originalPrice @currency(symbol: "$")
        discount @number(as: ".0%")
        weight @number(as: ".2f")
        dimensions @replace(old: "x", new: " × ")
        createdAt @date(format: "YYYY-MM-DD")
        lastModified @date(format: "time ago")
        reviews @shuffle {
          rating @number(as: ".1f")
          comment @strip @default(to: "No comment")
          createdAt @date(format: "MMM DD, YYYY")
        }
      }
    }
    ```

### User Profile Display

=== "Profile Query"

    ```graphql
    query GetUserProfile {
      user {
        username @lowercase
        displayName @default(to: "Anonymous User") @titleCase
        email @lowercase
        bio @default(to: "No bio available") @strip @capitalize
        location @titleCase
        website @lowercase
        socialLinks {
          twitter @replace(old: "https://twitter.com/", new: "@")
          linkedin @lowercase
        }
        joinDate @date(format: "MMMM YYYY")
        lastActive @date(format: "time ago")
        postCount @number(as: ",.0f")
        followerCount @number(as: ",.0f")
      }
    }
    ```

## Performance Considerations

!!! tip "Performance Tips"

    1. **Directive Order**: Directives are processed in order, so place expensive operations last
    2. **Caching**: Directive results aren't cached by default - consider caching formatted values
    3. **Complex Formatting**: For heavy date/time operations, consider pre-formatting in resolvers
    4. **List Operations**: Be cautious with shuffle/sample on very large lists

## Error Handling

Directives handle errors gracefully:

=== "Error Examples"

    ```graphql
    query {
      post {
        invalidDate @date(format: "YYYY-MM-DD")     # Returns "INVALID FORMAT STRING"
        nullValue @currency                         # Returns "$0.00"
        emptyString @default(to: "fallback")        # Returns "fallback"
      }
    }
    ```

## Best Practices

!!! tip "Directive Best Practices"

    1. **Use Defaults**: Always provide fallback values for nullable fields
    2. **Format Consistently**: Use the same date/number formats across your app
    3. **Chain Wisely**: Order directive chains logically (clean → transform → format)
    4. **Test Edge Cases**: Test with null, empty, and invalid values
    5. **Document Usage**: Document custom directive usage in your API documentation
    6. **Consider Performance**: Use directives for display formatting, not heavy processing

GraphQL directives in `graphene-django-extras` provide a powerful, flexible way to format and transform your API responses, making your GraphQL API more user-friendly and consistent across different client applications.
