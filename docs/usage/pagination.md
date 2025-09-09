# Pagination

Pagination is essential for managing large datasets in GraphQL APIs. `graphene-django-extras` provides several pagination strategies to efficiently handle query results and improve performance.

## Pagination Types

`graphene-django-extras` offers three pagination implementations:

- :material-format-list-numbered: **LimitOffsetGraphqlPagination**: Traditional limit/offset pagination
- :material-book-open-page-variant: **PageGraphqlPagination**: Page-number based pagination  
- :material-cursor-default: **CursorGraphqlPagination**: Cursor-based pagination (coming soon)

## LimitOffsetGraphqlPagination

The most common pagination method, using `limit` and `offset` parameters to control result sets.

### Features

- :material-speedometer: **Simple & Fast**: Easy to understand and implement
- :material-sort: **Flexible Ordering**: Supports custom ordering with Django syntax
- :material-tune: **Configurable Limits**: Set default and maximum page sizes
- :material-database: **Database Efficient**: Works well with Django QuerySets

### Basic Usage

=== "Define Pagination"

    ```python
    from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

    # Basic configuration
    pagination = LimitOffsetGraphqlPagination(
        default_limit=25,    # Default number of items per page
        max_limit=100,       # Maximum allowed limit
        ordering="-id"       # Default ordering
    )
    ```

=== "Use with DjangoListObjectType"

    ```python
    from graphene_django_extras import DjangoListObjectType
    from .models import User

    class UserListType(DjangoListObjectType):
        class Meta:
            model = User
            pagination = LimitOffsetGraphqlPagination(
                default_limit=25,
                max_limit=100,
                ordering="-date_joined"
            )
    ```

=== "Use with Fields"

    ```python
    from graphene_django_extras import DjangoFilterPaginateListField
    from .types import UserType

    class Query(graphene.ObjectType):
        users = DjangoFilterPaginateListField(
            UserType,
            pagination=LimitOffsetGraphqlPagination(default_limit=10)
        )
    ```

### Configuration Options

```python
LimitOffsetGraphqlPagination(
    default_limit=20,                    # Default items per page
    max_limit=100,                      # Maximum allowed limit
    ordering="-created_at",             # Default ordering field(s)
    limit_query_param="limit",          # GraphQL argument name for limit
    offset_query_param="offset",        # GraphQL argument name for offset
    ordering_param="ordering"           # GraphQL argument name for ordering
)
```

### Query Examples

=== "Basic Query"

    ```graphql
    query GetUsers {
      users {
        results {
          id
          username
          email
        }
        count
      }
    }
    ```

=== "With Pagination"

    ```graphql
    query GetUsersWithPagination {
      users(limit: 10, offset: 20) {
        results {
          id
          username  
          email
        }
        count
      }
    }
    ```

=== "With Ordering"

    ```graphql
    query GetUsersOrdered {
      users(limit: 10, ordering: "username,-date_joined") {
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

### Response Structure

```json
{
  "data": {
    "users": {
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

## PageGraphqlPagination

Page-number based pagination, similar to Django's built-in pagination.

### Features

- :material-book-multiple: **Page-Based**: Navigate by page numbers
- :material-resize: **Dynamic Page Size**: Optional client-controlled page sizes
- :material-calculator: **Automatic Calculation**: Handles page calculations automatically
- :material-navigation: **User Friendly**: Intuitive for frontend pagination controls

### Basic Usage

=== "Define Pagination"

    ```python
    from graphene_django_extras.paginations import PageGraphqlPagination

    pagination = PageGraphqlPagination(
        page_size=25,                    # Items per page
        page_size_query_param="pageSize", # Allow client to control page size
        max_page_size=100,               # Maximum page size
        ordering="-created_at"           # Default ordering
    )
    ```

=== "Use with Types"

    ```python
    class UserListType(DjangoListObjectType):
        class Meta:
            model = User
            pagination = PageGraphqlPagination(
                page_size=20,
                page_size_query_param="pageSize",
                max_page_size=100
            )
    ```

### Configuration Options

```python
PageGraphqlPagination(
    page_size=25,                       # Default page size
    page_size_query_param="pageSize",   # Enable dynamic page sizing
    max_page_size=100,                  # Maximum allowed page size
    ordering="-id",                     # Default ordering
    ordering_param="ordering"           # Ordering parameter name
)
```

!!! tip "Dynamic Page Size"
    Set `page_size_query_param` to allow clients to control page size. If not set, page size is fixed.

### Query Examples

=== "Basic Page Query"

    ```graphql
    query GetUsersPage {
      users(page: 1) {
        results {
          id
          username
          email
        }
        count
      }
    }
    ```

=== "With Dynamic Page Size"

    ```graphql
    query GetUsersWithPageSize {
      users(page: 2, pageSize: 15) {
        results {
          id
          username
          email
        }
        count
      }
    }
    ```

=== "Navigation Example"

    ```graphql
    query GetUsersForPagination {
      users(page: 3, pageSize: 20, ordering: "username") {
        results {
          id
          username
          email
          dateJoined
        }
        count
        # Calculate pagination info on frontend:
        # totalPages = Math.ceil(count / pageSize)
        # hasNextPage = page < totalPages
        # hasPreviousPage = page > 1
      }
    }
    ```

## Advanced Pagination Usage

### Multiple Ordering Fields

Both pagination types support multiple ordering fields:

=== "String Format"

    ```graphql
    query {
      users(ordering: "last_name,first_name,-date_joined") {
        results {
          firstName
          lastName
          dateJoined
        }
        count
      }
    }
    ```

=== "Django QuerySet Equivalent"

    ```python
    # This GraphQL query is equivalent to:
    User.objects.order_by('last_name', 'first_name', '-date_joined')
    ```

### Combining with Filtering

Pagination works seamlessly with filtering:

=== "Filtered Pagination"

    ```python
    class UserListType(DjangoListObjectType):
        class Meta:
            model = User
            pagination = LimitOffsetGraphqlPagination(default_limit=25)
            filter_fields = {
                'username': ('icontains', 'exact'),
                'email': ('icontains', 'exact'),
                'is_active': ('exact',),
            }
    ```

=== "Query with Filters"

    ```graphql
    query GetActiveUsers {
      users(
        isActive: true,
        username_Icontains: "john",
        limit: 10,
        ordering: "username"
      ) {
        results {
          id
          username
          email
          isActive
        }
        count
      }
    }
    ```

### Custom Pagination Classes

Create custom pagination for specific needs:

=== "Custom Limit/Offset"

    ```python
    from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

    class CustomPagination(LimitOffsetGraphqlPagination):
        def __init__(self, **kwargs):
            super().__init__(
                default_limit=50,
                max_limit=200,
                ordering="-updated_at",
                **kwargs
            )
    ```

=== "Custom Page Pagination"

    ```python
    from graphene_django_extras.paginations import PageGraphqlPagination

    class LargeDatasetPagination(PageGraphqlPagination):
        def __init__(self, **kwargs):
            super().__init__(
                page_size=100,
                page_size_query_param=None,  # Fixed page size
                max_page_size=100,
                ordering="-id",
                **kwargs
            )
    ```

## Performance Considerations

### Database Query Optimization

!!! warning "Count Queries"
    Pagination requires COUNT queries which can be expensive on large datasets. Consider caching count results for better performance.

=== "Efficient Ordering"

    ```python
    # ✅ Good: Use indexed fields for ordering
    pagination = LimitOffsetGraphqlPagination(
        ordering="-id"  # Primary key is indexed
    )

    # ⚠️  Less efficient: Non-indexed field
    pagination = LimitOffsetGraphqlPagination(
        ordering="full_name"  # May not be indexed
    )
    ```

=== "Select Related"

    ```python
    # Optimize with select_related for foreign keys
    class UserListType(DjangoListObjectType):
        class Meta:
            model = User
            pagination = LimitOffsetGraphqlPagination(default_limit=25)

        @classmethod
        def get_queryset(cls, queryset, info):
            return queryset.select_related('profile')
    ```

### Large Offset Performance

!!! info "Offset Limitations"
    Large offsets (e.g., `offset=10000`) can be slow. Consider cursor-based pagination for very large datasets.

## Frontend Integration

### React Example with Apollo Client

=== "Limit/Offset Pagination"

    ```javascript
    import { gql, useQuery } from '@apollo/client';

    const GET_USERS = gql`
      query GetUsers($limit: Int!, $offset: Int!) {
        users(limit: $limit, offset: $offset) {
          results {
            id
            username
            email
          }
          count
        }
      }
    `;

    function UserList() {
      const [page, setPage] = useState(0);
      const limit = 10;
      const offset = page * limit;

      const { loading, error, data } = useQuery(GET_USERS, {
        variables: { limit, offset }
      });

      const totalPages = data ? Math.ceil(data.users.count / limit) : 0;

      return (
        <div>
          {data?.users.results.map(user => (
            <div key={user.id}>{user.username}</div>
          ))}
          
          <Pagination
            currentPage={page}
            totalPages={totalPages}
            onPageChange={setPage}
          />
        </div>
      );
    }
    ```

=== "Page-Based Pagination"

    ```javascript
    const GET_USERS_BY_PAGE = gql`
      query GetUsers($page: Int!, $pageSize: Int) {
        users(page: $page, pageSize: $pageSize) {
          results {
            id
            username
            email
          }
          count
        }
      }
    `;

    function UserList() {
      const [currentPage, setCurrentPage] = useState(1);
      const pageSize = 15;

      const { loading, error, data } = useQuery(GET_USERS_BY_PAGE, {
        variables: { page: currentPage, pageSize }
      });

      const totalPages = data ? Math.ceil(data.users.count / pageSize) : 0;

      return (
        <div>
          {data?.users.results.map(user => (
            <div key={user.id}>{user.username}</div>
          ))}
          
          <div>
            <button 
              disabled={currentPage <= 1}
              onClick={() => setCurrentPage(currentPage - 1)}
            >
              Previous
            </button>
            
            <span>Page {currentPage} of {totalPages}</span>
            
            <button 
              disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage(currentPage + 1)}
            >
              Next
            </button>
          </div>
        </div>
      );
    }
    ```

## Best Practices

!!! tip "Pagination Best Practices"

    1. **Set Reasonable Defaults**: Use sensible default page sizes (10-50 items)
    2. **Limit Maximum Size**: Prevent excessive data transfer with max limits
    3. **Use Indexed Fields**: Order by indexed fields for better performance  
    4. **Cache Counts**: Cache total counts for frequently accessed datasets
    5. **Consider Cursor Pagination**: For real-time data or very large datasets
    6. **Frontend State Management**: Maintain pagination state in your frontend

### Security Considerations

```python
# Limit maximum page sizes to prevent abuse
pagination = LimitOffsetGraphqlPagination(
    default_limit=25,
    max_limit=100,  # Prevent users from requesting thousands of records
    ordering="-id"
)
```

### Testing Pagination

=== "Test Pagination Logic"

    ```python
    import pytest
    from graphene.test import Client
    from .schema import schema

    @pytest.mark.django_db
    def test_users_pagination():
        # Create test users
        for i in range(50):
            User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com'
            )

        client = Client(schema)
        query = """
            query GetUsers($limit: Int!, $offset: Int!) {
                users(limit: $limit, offset: $offset) {
                    results {
                        id
                        username
                    }
                    count
                }
            }
        """

        result = client.execute(query, variables={'limit': 10, 'offset': 20})
        
        assert len(result['data']['users']['results']) == 10
        assert result['data']['users']['count'] == 50
    ```

=== "Test Ordering"

    ```python
    @pytest.mark.django_db
    def test_users_ordering():
        User.objects.create_user(username='charlie', email='c@example.com')
        User.objects.create_user(username='alice', email='a@example.com') 
        User.objects.create_user(username='bob', email='b@example.com')

        client = Client(schema)
        query = """
            query GetUsers($ordering: String!) {
                users(ordering: $ordering, limit: 10) {
                    results {
                        username
                    }
                }
            }
        """

        result = client.execute(query, variables={'ordering': 'username'})
        usernames = [user['username'] for user in result['data']['users']['results']]
        
        assert usernames == ['alice', 'bob', 'charlie']
    ```

The pagination system in `graphene-django-extras` provides flexible, efficient ways to handle large datasets while maintaining good performance and user experience.