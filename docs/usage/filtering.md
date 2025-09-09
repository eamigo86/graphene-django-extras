# Filtering

Filtering allows clients to request specific subsets of data based on field values and conditions. `graphene-django-extras` provides powerful filtering capabilities built on top of `django-filter`, making it easy to create flexible and efficient GraphQL queries.

## Overview

The filtering system in `graphene-django-extras` provides:

- :material-filter: **Field-Based Filtering**: Filter by any model field
- :material-tune-vertical: **Multiple Lookup Types**: Support for various comparison operations
- :material-link: **Related Field Filtering**: Filter across relationships
- :material-code-tags: **Custom FilterSets**: Advanced filtering with django-filter
- :material-lightning-bolt: **Automatic GraphQL Integration**: Seamless schema generation

## Basic Field Filtering

The simplest way to add filtering is through the `filter_fields` meta option:

=== "Simple Filtering"

    ```python
    from graphene_django_extras import DjangoObjectType, DjangoListObjectType

    class UserType(DjangoObjectType):
        class Meta:
            model = User
            filter_fields = ['username', 'email', 'is_active']

    class UserListType(DjangoListObjectType):
        class Meta:
            model = User
            filter_fields = ['username', 'email', 'is_active']
    ```

=== "Query Example"

    ```graphql
    query GetUsers {
      users(username: "john", isActive: true) {
        results {
          id
          username
          email
          isActive
        }
      }
    }
    ```

## Lookup Types

Control how fields are filtered with lookup types:

=== "Multiple Lookups"

    ```python
    class UserType(DjangoObjectType):
        class Meta:
            model = User
            filter_fields = {
                'username': ('exact', 'icontains', 'iexact'),
                'email': ('exact', 'icontains'),
                'date_joined': ('exact', 'lt', 'gt', 'lte', 'gte'),
                'is_active': ('exact',),
            }
    ```

=== "Available Lookup Types"

    | Lookup | Description | Example |
    |--------|-------------|---------|
    | `exact` | Exact match | `username: "john"` |
    | `iexact` | Case-insensitive exact match | `username_Iexact: "JOHN"` |
    | `contains` | Contains substring | `username_Contains: "oh"` |
    | `icontains` | Case-insensitive contains | `username_Icontains: "OH"` |
    | `startswith` | Starts with | `username_Startswith: "jo"` |
    | `endswith` | Ends with | `username_Endswith: "hn"` |
    | `lt` | Less than | `age_Lt: 30` |
    | `lte` | Less than or equal | `age_Lte: 30` |
    | `gt` | Greater than | `age_Gt: 18` |
    | `gte` | Greater than or equal | `age_Gte: 18` |
    | `in` | In list | `id_In: [1, 2, 3]` |
    | `isnull` | Is null/not null | `email_Isnull: true` |

=== "Query with Lookups"

    ```graphql
    query SearchUsers {
      users(
        username_Icontains: "john",
        dateJoined_Gte: "2023-01-01",
        isActive: true
      ) {
        results {
          id
          username
          email
          dateJoined
        }
      }
    }
    ```

## Related Field Filtering

Filter across model relationships using double underscores:

=== "Models"

    ```python
    class Profile(models.Model):
        user = models.OneToOneField(User, on_delete=models.CASCADE)
        bio = models.TextField(blank=True)
        location = models.CharField(max_length=100, blank=True)
        birth_date = models.DateField(null=True, blank=True)

    class Post(models.Model):
        title = models.CharField(max_length=200)
        content = models.TextField()
        author = models.ForeignKey(User, on_delete=models.CASCADE)
        category = models.ForeignKey(Category, on_delete=models.CASCADE)
        created_at = models.DateTimeField(auto_now_add=True)
    ```

=== "Related Field Filtering"

    ```python
    class PostType(DjangoObjectType):
        class Meta:
            model = Post
            filter_fields = {
                'title': ('icontains', 'exact'),
                'content': ('icontains',),
                'created_at': ('exact', 'lt', 'gt', 'lte', 'gte'),
                # Filter by author fields
                'author__username': ('icontains', 'exact'),
                'author__email': ('exact',),
                'author__is_active': ('exact',),
                # Filter by author's profile
                'author__profile__location': ('icontains', 'exact'),
                'author__profile__birth_date': ('exact', 'lt', 'gt'),
                # Filter by category
                'category__name': ('icontains', 'exact'),
                'category__slug': ('exact',),
            }
    ```

=== "Query Related Fields"

    ```graphql
    query GetPostsByAuthorLocation {
      posts(
        author_Profile_Location_Icontains: "new york",
        category_Name: "Technology",
        createdAt_Gte: "2023-01-01"
      ) {
        results {
          id
          title
          author {
            username
            profile {
              location
            }
          }
          category {
            name
          }
        }
      }
    }
    ```

## Custom FilterSets

For advanced filtering needs, use django-filter FilterSets:

=== "Custom FilterSet"

    ```python
    import django_filters
    from django_filters import FilterSet, filters
    from django.contrib.auth.models import User

    class UserFilterSet(FilterSet):
        # Custom filter for name search across multiple fields
        name = filters.CharFilter(method='filter_name', label='Name')

        # Date range filter
        joined_after = filters.DateFilter(
            field_name='date_joined',
            lookup_expr='gte'
        )
        joined_before = filters.DateFilter(
            field_name='date_joined',
            lookup_expr='lte'
        )

        # Custom choice filter
        user_type = filters.ChoiceFilter(
            choices=[('staff', 'Staff'), ('regular', 'Regular')],
            method='filter_user_type'
        )

        class Meta:
            model = User
            fields = {
                'username': ['exact', 'icontains'],
                'email': ['exact', 'icontains'],
                'is_active': ['exact'],
            }

        def filter_name(self, queryset, name, value):
            """Search across first_name and last_name."""
            return queryset.filter(
                Q(first_name__icontains=value) |
                Q(last_name__icontains=value)
            )

        def filter_user_type(self, queryset, name, value):
            """Filter by user type."""
            if value == 'staff':
                return queryset.filter(is_staff=True)
            elif value == 'regular':
                return queryset.filter(is_staff=False)
            return queryset
    ```

=== "Use Custom FilterSet"

    ```python
    from .filtersets import UserFilterSet

    class UserType(DjangoObjectType):
        class Meta:
            model = User
            filterset_class = UserFilterSet

    # Or with DjangoListObjectType
    class UserListType(DjangoListObjectType):
        class Meta:
            model = User
            filterset_class = UserFilterSet
    ```

=== "Query Custom Filters"

    ```graphql
    query SearchUsers {
      users(
        name: "john",
        userType: "staff",
        joinedAfter: "2023-01-01",
        username_Icontains: "admin"
      ) {
        results {
          id
          username
          firstName
          lastName
          isStaff
          dateJoined
        }
      }
    }
    ```

## Combining Filtering with Other Features

### Filtering + Pagination

Combine filtering with pagination for efficient data access:

=== "Filtered Paginated Type"

    ```python
    from graphene_django_extras import DjangoListObjectType
    from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

    class UserListType(DjangoListObjectType):
        class Meta:
            model = User
            pagination = LimitOffsetGraphqlPagination(default_limit=25)
            filter_fields = {
                'username': ('icontains', 'exact'),
                'email': ('icontains', 'exact'),
                'is_active': ('exact',),
                'date_joined': ('exact', 'lt', 'gt', 'lte', 'gte'),
            }
    ```

=== "Query with Filter + Pagination"

    ```graphql
    query GetActiveUsers {
      users(
        isActive: true,
        username_Icontains: "john",
        limit: 10,
        offset: 20,
        ordering: "-date_joined"
      ) {
        results {
          id
          username
          email
          dateJoined
        }
        count
      }
    }
    ```

### Filtering + Ordering

=== "Ordered Filtered Results"

    ```graphql
    query GetUsersOrderedFiltered {
      users(
        isActive: true,
        dateJoined_Gte: "2023-01-01",
        ordering: "username,-date_joined",
        limit: 20
      ) {
        results {
          username
          dateJoined
          email
        }
        count
      }
    }
    ```

## Field-Level Filtering

Use fields for more granular control:

=== "DjangoFilterListField"

    ```python
    import graphene
    from graphene_django_extras import DjangoFilterListField

    class Query(graphene.ObjectType):
        # Basic filtering field
        all_users = DjangoFilterListField(UserType)

        # Filtering with custom filterset
        staff_users = DjangoFilterListField(
            UserType,
            filterset_class=UserFilterSet
        )

        # Custom resolver with filtering
        active_users = DjangoFilterListField(UserType)

        def resolve_active_users(self, info, **kwargs):
            return User.objects.filter(is_active=True)
    ```

=== "DjangoFilterPaginateListField"

    ```python
    from graphene_django_extras import DjangoFilterPaginateListField
    from graphene_django_extras.paginations import PageGraphqlPagination

    class Query(graphene.ObjectType):
        users = DjangoFilterPaginateListField(
            UserType,
            pagination=PageGraphqlPagination(page_size=20),
            filterset_class=UserFilterSet,
            description="Paginated and filtered user list"
        )
    ```

## Advanced Filtering Techniques

### Custom Filter Methods

=== "Complex Filter Logic"

    ```python
    class PostFilterSet(FilterSet):
        # Filter by multiple categories
        categories = filters.ModelMultipleChoiceFilter(
            field_name='category',
            queryset=Category.objects.all(),
            conjoined=False  # OR logic instead of AND
        )

        # Search across multiple text fields
        search = filters.CharFilter(method='filter_search')

        # Filter by author's profile data
        author_location = filters.CharFilter(
            field_name='author__profile__location',
            lookup_expr='icontains'
        )

        class Meta:
            model = Post
            fields = ['title', 'created_at']

        def filter_search(self, queryset, name, value):
            """Search across title and content."""
            return queryset.filter(
                Q(title__icontains=value) |
                Q(content__icontains=value)
            )
    ```

### Range Filters

=== "Date and Number Ranges"

    ```python
    class ProductFilterSet(FilterSet):
        price_range = filters.RangeFilter(field_name='price')
        created_range = filters.DateFromToRangeFilter(field_name='created_at')

        class Meta:
            model = Product
            fields = ['name', 'category']
    ```

=== "Range Query"

    ```graphql
    query GetProducts {
      products(
        priceRange_0: 10.00,
        priceRange_1: 100.00,
        createdRange_0: "2023-01-01",
        createdRange_1: "2023-12-31"
      ) {
        results {
          id
          name
          price
          createdAt
        }
      }
    }
    ```

## Performance Optimization

### Database Indexing

!!! tip "Index Filter Fields"
    Add database indexes to commonly filtered fields for better performance.

```python
class User(models.Model):
    username = models.CharField(max_length=150, unique=True, db_index=True)
    email = models.EmailField(db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    date_joined = models.DateTimeField(auto_now_add=True, db_index=True)
```

### Query Optimization

=== "Select Related"

    ```python
    class PostListType(DjangoListObjectType):
        class Meta:
            model = Post
            filter_fields = {
                'title': ('icontains',),
                'author__username': ('icontains',),
                'category__name': ('exact',),
            }

        @classmethod
        def get_queryset(cls, queryset, info):
            return queryset.select_related('author', 'category')
    ```

=== "Prefetch Related"

    ```python
    class UserListType(DjangoListObjectType):
        class Meta:
            model = User
            filter_fields = ['username', 'email']

        @classmethod
        def get_queryset(cls, queryset, info):
            return queryset.prefetch_related('posts', 'profile')
    ```

## Error Handling

Handle filtering errors gracefully:

=== "Custom Filter Validation"

    ```python
    class CustomUserFilterSet(FilterSet):
        age = filters.NumberFilter(method='filter_age')

        class Meta:
            model = User
            fields = ['username', 'email']

        def filter_age(self, queryset, name, value):
            if value < 0:
                raise ValueError("Age cannot be negative")
            # Calculate age from birth_date
            from datetime import date
            cutoff_date = date.today() - timedelta(days=365 * value)
            return queryset.filter(profile__birth_date__lte=cutoff_date)
    ```

## Testing Filtering

=== "Filter Tests"

    ```python
    import pytest
    from graphene.test import Client
    from .schema import schema

    @pytest.mark.django_db
    def test_user_filtering():
        # Create test data
        active_user = User.objects.create_user(
            username='active_user',
            email='active@example.com',
            is_active=True
        )
        inactive_user = User.objects.create_user(
            username='inactive_user',
            email='inactive@example.com',
            is_active=False
        )

        client = Client(schema)
        query = """
            query GetActiveUsers {
                users(isActive: true) {
                    results {
                        id
                        username
                        isActive
                    }
                }
            }
        """

        result = client.execute(query)
        users = result['data']['users']['results']

        assert len(users) == 1
        assert users[0]['username'] == 'active_user'
        assert users[0]['isActive'] is True
    ```

=== "Complex Filter Tests"

    ```python
    @pytest.mark.django_db
    def test_related_field_filtering():
        # Create test data with relationships
        category = Category.objects.create(name='Technology')
        user = User.objects.create_user(username='author', email='author@example.com')
        Post.objects.create(
            title='Django GraphQL',
            content='Advanced GraphQL techniques',
            author=user,
            category=category
        )

        client = Client(schema)
        query = """
            query GetTechPosts {
                posts(category_Name: "Technology", title_Icontains: "Django") {
                    results {
                        title
                        category {
                            name
                        }
                    }
                }
            }
        """

        result = client.execute(query)
        posts = result['data']['posts']['results']

        assert len(posts) == 1
        assert posts[0]['title'] == 'Django GraphQL'
        assert posts[0]['category']['name'] == 'Technology'
    ```

## Best Practices

!!! tip "Filtering Best Practices"

    1. **Index Filter Fields**: Add database indexes to frequently filtered fields
    2. **Limit Filter Options**: Don't expose sensitive fields for filtering
    3. **Use Related Queries**: Optimize with `select_related` and `prefetch_related`
    4. **Validate Input**: Add validation for custom filter methods
    5. **Test Edge Cases**: Test filtering with edge cases and invalid input
    6. **Document Filters**: Provide clear descriptions for custom filters

### Security Considerations

```python
class SecureUserFilterSet(FilterSet):
    class Meta:
        model = User
        # Don't expose sensitive fields
        fields = {
            'username': ['icontains', 'exact'],
            'is_active': ['exact'],
            # Exclude: password, last_login, user_permissions, etc.
        }
```

The filtering system in `graphene-django-extras` provides powerful and flexible ways to query your data, making it easy to build efficient GraphQL APIs with Django.
