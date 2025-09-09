# Examples

This section provides comprehensive examples showing how to use `graphene-django-extras` in real-world scenarios. These examples demonstrate queries, mutations, filtering, pagination, and directives working together.

## Sample Application Setup

Let's start with a blog application to demonstrate the features:

=== "models.py"

    ```python
    from django.db import models
    from django.contrib.auth.models import User

    class Category(models.Model):
        name = models.CharField(max_length=100)
        slug = models.SlugField(unique=True)
        description = models.TextField(blank=True)
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return self.name

    class Tag(models.Model):
        name = models.CharField(max_length=50)
        color = models.CharField(max_length=7, default="#000000")  # Hex color

        def __str__(self):
            return self.name

    class Post(models.Model):
        STATUS_CHOICES = [
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('archived', 'Archived'),
        ]

        title = models.CharField(max_length=200)
        slug = models.SlugField(unique=True)
        content = models.TextField()
        excerpt = models.TextField(blank=True)
        status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
        author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
        category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
        tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
        featured_image = models.ImageField(upload_to='posts/', blank=True)
        view_count = models.PositiveIntegerField(default=0)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
        published_at = models.DateTimeField(null=True, blank=True)

        class Meta:
            ordering = ['-created_at']

        def __str__(self):
            return self.title

    class Comment(models.Model):
        post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
        author = models.ForeignKey(User, on_delete=models.CASCADE)
        content = models.TextField()
        parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
        is_approved = models.BooleanField(default=False)
        created_at = models.DateTimeField(auto_now_add=True)

        class Meta:
            ordering = ['created_at']

        def __str__(self):
            return f"Comment by {self.author.username} on {self.post.title}"

    class UserProfile(models.Model):
        user = models.OneToOneField(User, on_delete=models.CASCADE)
        bio = models.TextField(blank=True)
        avatar = models.ImageField(upload_to='avatars/', blank=True)
        website = models.URLField(blank=True)
        location = models.CharField(max_length=100, blank=True)
        birth_date = models.DateField(null=True, blank=True)
        social_links = models.JSONField(default=dict, blank=True)

        def __str__(self):
            return f"{self.user.username}'s Profile"
    ```

=== "serializers.py"

    ```python
    from rest_framework import serializers
    from django.contrib.auth.models import User
    from .models import Category, Tag, Post, Comment, UserProfile

    class UserProfileSerializer(serializers.ModelSerializer):
        class Meta:
            model = UserProfile
            fields = ['bio', 'avatar', 'website', 'location', 'birth_date', 'social_links']

    class UserSerializer(serializers.ModelSerializer):
        password = serializers.CharField(write_only=True)

        class Meta:
            model = User
            fields = ['username', 'email', 'first_name', 'last_name', 'password']

        def create(self, validated_data):
            password = validated_data.pop('password')
            user = User(**validated_data)
            user.set_password(password)
            user.save()
            return user

    class CategorySerializer(serializers.ModelSerializer):
        class Meta:
            model = Category
            fields = ['name', 'slug', 'description']

    class TagSerializer(serializers.ModelSerializer):
        class Meta:
            model = Tag
            fields = ['name', 'color']

    class PostSerializer(serializers.ModelSerializer):
        class Meta:
            model = Post
            fields = [
                'title', 'slug', 'content', 'excerpt', 'status',
                'category', 'tags', 'featured_image'
            ]

    class CommentSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ['content', 'parent']
    ```

=== "types.py"

    ```python
    from graphene_django_extras import (
        DjangoObjectType, DjangoListObjectType, DjangoSerializerType
    )
    from graphene_django_extras.paginations import (
        LimitOffsetGraphqlPagination, PageGraphqlPagination
    )
    from django.contrib.auth.models import User
    from .models import Category, Tag, Post, Comment, UserProfile
    from .serializers import (
        UserSerializer, CategorySerializer, TagSerializer,
        PostSerializer, CommentSerializer
    )
    from .filtersets import PostFilterSet, UserFilterSet

    # Basic Object Types
    class UserType(DjangoObjectType):
        class Meta:
            model = User
            description = "User type with basic information"
            filter_fields = {
                'username': ('exact', 'icontains'),
                'email': ('exact', 'icontains'),
                'first_name': ('icontains',),
                'last_name': ('icontains',),
                'is_active': ('exact',),
                'date_joined': ('exact', 'gte', 'lte'),
            }

    class CategoryType(DjangoObjectType):
        class Meta:
            model = Category
            description = "Blog category"
            filter_fields = {
                'name': ('exact', 'icontains'),
                'slug': ('exact',),
            }

    class TagType(DjangoObjectType):
        class Meta:
            model = Tag
            description = "Post tag"
            filter_fields = ['name', 'color']

    class UserProfileType(DjangoObjectType):
        class Meta:
            model = UserProfile
            description = "Extended user profile information"

    class CommentType(DjangoObjectType):
        class Meta:
            model = Comment
            description = "Post comment"
            filter_fields = {
                'author__username': ('exact', 'icontains'),
                'is_approved': ('exact',),
                'created_at': ('exact', 'gte', 'lte'),
            }

    class PostType(DjangoObjectType):
        class Meta:
            model = Post
            description = "Blog post with full content and metadata"
            filter_fields = {
                'title': ('exact', 'icontains'),
                'status': ('exact',),
                'author__username': ('exact', 'icontains'),
                'category__name': ('exact', 'icontains'),
                'tags__name': ('exact', 'icontains'),
                'created_at': ('exact', 'gte', 'lte'),
                'published_at': ('exact', 'gte', 'lte'),
            }

    # List Object Types with Pagination
    class PostListType(DjangoListObjectType):
        class Meta:
            model = Post
            description = "Paginated list of blog posts"
            pagination = LimitOffsetGraphqlPagination(
                default_limit=10,
                max_limit=50,
                ordering="-published_at"
            )
            filterset_class = PostFilterSet

    class UserListType(DjangoListObjectType):
        class Meta:
            model = User
            description = "Paginated list of users"
            pagination = PageGraphqlPagination(
                page_size=20,
                page_size_query_param="pageSize"
            )
            filterset_class = UserFilterSet

    class CommentListType(DjangoListObjectType):
        class Meta:
            model = Comment
            description = "Paginated list of comments"
            pagination = LimitOffsetGraphqlPagination(default_limit=25)

    # Serializer Types for CRUD Operations
    class UserSerializerType(DjangoSerializerType):
        class Meta:
            serializer_class = UserSerializer
            description = "User operations with serializer validation"
            pagination = LimitOffsetGraphqlPagination(default_limit=25)
            filterset_class = UserFilterSet

    class PostSerializerType(DjangoSerializerType):
        class Meta:
            serializer_class = PostSerializer
            description = "Post operations with serializer validation"
            pagination = LimitOffsetGraphqlPagination(default_limit=10)
            filterset_class = PostFilterSet
    ```

=== "mutations.py"

    ```python
    from graphene_django_extras import DjangoSerializerMutation
    from .serializers import (
        UserSerializer, CategorySerializer, TagSerializer,
        PostSerializer, CommentSerializer
    )

    class UserMutation(DjangoSerializerMutation):
        class Meta:
            serializer_class = UserSerializer
            description = "User CRUD operations"
            nested_fields = {
                'profile': UserProfileSerializer
            }

    class CategoryMutation(DjangoSerializerMutation):
        class Meta:
            serializer_class = CategorySerializer
            description = "Category CRUD operations"

    class TagMutation(DjangoSerializerMutation):
        class Meta:
            serializer_class = TagSerializer
            description = "Tag CRUD operations"

    class PostMutation(DjangoSerializerMutation):
        class Meta:
            serializer_class = PostSerializer
            description = "Post CRUD operations"
            exclude_fields = ('view_count',)  # Don't allow direct manipulation

    class CommentMutation(DjangoSerializerMutation):
        class Meta:
            serializer_class = CommentSerializer
            description = "Comment CRUD operations"
    ```

=== "filtersets.py"

    ```python
    import django_filters
    from django_filters import FilterSet, filters
    from django.contrib.auth.models import User
    from django.db.models import Q
    from .models import Post, Category, Tag

    class UserFilterSet(FilterSet):
        # Custom name search across first_name and last_name
        name = filters.CharFilter(method='filter_name', label='Name')

        # Date joined ranges
        joined_after = filters.DateFilter(field_name='date_joined', lookup_expr='gte')
        joined_before = filters.DateFilter(field_name='date_joined', lookup_expr='lte')

        # User type filter
        user_type = filters.ChoiceFilter(
            choices=[('staff', 'Staff'), ('regular', 'Regular'), ('superuser', 'Superuser')],
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
            return queryset.filter(
                Q(first_name__icontains=value) | Q(last_name__icontains=value)
            )

        def filter_user_type(self, queryset, name, value):
            if value == 'staff':
                return queryset.filter(is_staff=True, is_superuser=False)
            elif value == 'regular':
                return queryset.filter(is_staff=False, is_superuser=False)
            elif value == 'superuser':
                return queryset.filter(is_superuser=True)
            return queryset

    class PostFilterSet(FilterSet):
        # Content search across title and content
        search = filters.CharFilter(method='filter_search', label='Search')

        # Date ranges
        created_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
        created_before = filters.DateFilter(field_name='created_at', lookup_expr='lte')
        published_after = filters.DateFilter(field_name='published_at', lookup_expr='gte')
        published_before = filters.DateFilter(field_name='published_at', lookup_expr='lte')

        # Multiple categories
        categories = filters.ModelMultipleChoiceFilter(
            field_name='category',
            queryset=Category.objects.all()
        )

        # Multiple tags
        tags = filters.ModelMultipleChoiceFilter(
            field_name='tags',
            queryset=Tag.objects.all()
        )

        # View count ranges
        min_views = filters.NumberFilter(field_name='view_count', lookup_expr='gte')
        max_views = filters.NumberFilter(field_name='view_count', lookup_expr='lte')

        class Meta:
            model = Post
            fields = {
                'status': ['exact'],
                'author__username': ['exact', 'icontains'],
            }

        def filter_search(self, queryset, name, value):
            return queryset.filter(
                Q(title__icontains=value) |
                Q(content__icontains=value) |
                Q(excerpt__icontains=value)
            )
    ```

=== "schema.py"

    ```python
    import graphene
    from graphene_django_extras import (
        DjangoObjectField, DjangoFilterListField,
        DjangoFilterPaginateListField, DjangoListObjectField,
        all_directives
    )
    from .types import (
        UserType, CategoryType, TagType, PostType, CommentType,
        UserListType, PostListType, CommentListType,
        UserSerializerType, PostSerializerType
    )
    from .mutations import (
        UserMutation, CategoryMutation, TagMutation,
        PostMutation, CommentMutation
    )

    class Query(graphene.ObjectType):
        # Single object queries
        user = DjangoObjectField(UserType, description="Get a single user")
        post = DjangoObjectField(PostType, description="Get a single post")
        category = DjangoObjectField(CategoryType, description="Get a single category")
        tag = DjangoObjectField(TagType, description="Get a single tag")
        comment = DjangoObjectField(CommentType, description="Get a single comment")

        # List queries with different approaches
        all_posts = DjangoListObjectField(PostListType, description="All posts with pagination")
        all_users = DjangoListObjectField(UserListType, description="All users with pagination")
        all_comments = DjangoListObjectField(CommentListType, description="All comments with pagination")

        # Filter-only lists (no pagination)
        posts = DjangoFilterListField(PostType, description="Filter posts without pagination")
        users = DjangoFilterListField(UserType, description="Filter users without pagination")
        categories = DjangoFilterListField(CategoryType, description="All categories")
        tags = DjangoFilterListField(TagType, description="All tags")

        # Filtered and paginated lists
        posts_paginated = DjangoFilterPaginateListField(
            PostType,
            pagination=LimitOffsetGraphqlPagination(default_limit=10),
            description="Posts with filtering and pagination"
        )

        # Serializer-based queries
        user_serializer, users_serializer = UserSerializerType.QueryFields()
        post_serializer, posts_serializer = PostSerializerType.QueryFields()

    class Mutation(graphene.ObjectType):
        # User mutations
        create_user, delete_user, update_user = UserMutation.MutationFields()

        # Category mutations
        create_category, delete_category, update_category = CategoryMutation.MutationFields()

        # Tag mutations
        create_tag, delete_tag, update_tag = TagMutation.MutationFields()

        # Post mutations
        create_post, delete_post, update_post = PostMutation.MutationFields()

        # Comment mutations
        create_comment, delete_comment, update_comment = CommentMutation.MutationFields()

    schema = graphene.Schema(
        query=Query,
        mutation=Mutation,
        directives=all_directives
    )
    ```

## Query Examples

Now let's explore various query examples using our blog application:

### Basic Object Queries

=== "Get Single Post"

    ```graphql
    query GetPost($id: ID!) {
      post(id: $id) {
        id
        title
        slug
        content
        status
        viewCount
        createdAt
        author {
          id
          username
          firstName
          lastName
          profile {
            bio
            avatar
            location
          }
        }
        category {
          id
          name
          slug
          description
        }
        tags {
          id
          name
          color
        }
        comments {
          id
          content
          author {
            username
          }
          createdAt
          isApproved
          parent {
            id
            content
          }
        }
      }
    }
    ```

=== "Response"

    ```json
    {
      "data": {
        "post": {
          "id": "1",
          "title": "Getting Started with GraphQL and Django",
          "slug": "getting-started-graphql-django",
          "content": "GraphQL is a powerful query language...",
          "status": "published",
          "viewCount": 1245,
          "createdAt": "2023-12-01T10:30:00",
          "author": {
            "id": "1",
            "username": "john_doe",
            "firstName": "John",
            "lastName": "Doe",
            "profile": {
              "bio": "Full-stack developer passionate about GraphQL",
              "avatar": "/media/avatars/john.jpg",
              "location": "San Francisco, CA"
            }
          },
          "category": {
            "id": "1",
            "name": "Technology",
            "slug": "technology",
            "description": "Latest in tech trends and tutorials"
          },
          "tags": [
            {
              "id": "1",
              "name": "GraphQL",
              "color": "#e10098"
            },
            {
              "id": "2",
              "name": "Django",
              "color": "#092e20"
            }
          ],
          "comments": [
            {
              "id": "1",
              "content": "Great tutorial! Very helpful.",
              "author": {
                "username": "reader1"
              },
              "createdAt": "2023-12-01T14:20:00",
              "isApproved": true,
              "parent": null
            }
          ]
        }
      }
    }
    ```

### Filtered Lists

=== "Filter Posts by Category and Status"

    ```graphql
    query GetTechPosts {
      posts(
        status: "published",
        category_Name: "Technology",
        createdAt_Gte: "2023-01-01"
      ) {
        id
        title
        excerpt
        author {
          username
        }
        createdAt
        viewCount
      }
    }
    ```

=== "Search Posts"

    ```graphql
    query SearchPosts($searchTerm: String!) {
      allPosts(
        search: $searchTerm,
        status: "published",
        limit: 10,
        ordering: "-view_count"
      ) {
        results {
          id
          title
          excerpt
          viewCount
          author {
            username
          }
          category {
            name
          }
        }
        count
      }
    }
    ```

=== "Filter by Multiple Tags"

    ```graphql
    query GetPostsByTags {
      allPosts(
        tags: ["1", "3", "5"],  # GraphQL, React, Python
        status: "published",
        limit: 20
      ) {
        results {
          id
          title
          tags {
            name
            color
          }
        }
        count
      }
    }
    ```

### Paginated Queries

=== "Limit/Offset Pagination"

    ```graphql
    query GetPostsPaginated($limit: Int!, $offset: Int!) {
      allPosts(
        limit: $limit,
        offset: $offset,
        status: "published",
        ordering: "-published_at"
      ) {
        results {
          id
          title
          excerpt
          publishedAt
          author {
            username
          }
          category {
            name
          }
          viewCount
        }
        count
      }
    }
    ```

=== "Page-Based Pagination"

    ```graphql
    query GetUsersPage($page: Int!, $pageSize: Int) {
      allUsers(page: $page, pageSize: $pageSize, isActive: true) {
        results {
          id
          username
          firstName
          lastName
          email
          dateJoined
          profile {
            location
            website
          }
        }
        count
      }
    }
    ```

### Complex Filtering

=== "Advanced Post Search"

    ```graphql
    query AdvancedPostSearch(
      $search: String,
      $categories: [ID!],
      $tags: [ID!],
      $authorName: String,
      $minViews: Int,
      $publishedAfter: Date,
      $publishedBefore: Date
    ) {
      allPosts(
        search: $search,
        categories: $categories,
        tags: $tags,
        author_Username_Icontains: $authorName,
        minViews: $minViews,
        publishedAfter: $publishedAfter,
        publishedBefore: $publishedBefore,
        status: "published",
        limit: 20,
        ordering: "-published_at"
      ) {
        results {
          id
          title
          excerpt
          publishedAt
          viewCount
          author {
            username
            firstName
            lastName
          }
          category {
            name
            slug
          }
          tags {
            name
            color
          }
        }
        count
      }
    }
    ```

=== "Variables"

    ```json
    {
      "search": "GraphQL Django",
      "categories": ["1", "2"],
      "tags": ["1", "3"],
      "authorName": "john",
      "minViews": 100,
      "publishedAfter": "2023-01-01",
      "publishedBefore": "2023-12-31"
    }
    ```

## Mutation Examples

### Creating Records

=== "Create User with Profile"

    ```graphql
    mutation CreateUserWithProfile($userData: UserInput!, $profileData: UserProfileInput!) {
      createUser(newUser: $userData, profile: $profileData) {
        ok
        user {
          id
          username
          email
          firstName
          lastName
          profile {
            bio
            location
            website
          }
        }
        errors {
          field
          messages
        }
      }
    }
    ```

=== "Variables"

    ```json
    {
      "userData": {
        "username": "newuser123",
        "email": "newuser@example.com",
        "firstName": "Jane",
        "lastName": "Smith",
        "password": "securePassword123"
      },
      "profileData": {
        "bio": "I'm a web developer passionate about modern technologies",
        "location": "New York, NY",
        "website": "https://janesmith.dev"
      }
    }
    ```

=== "Create Post"

    ```graphql
    mutation CreatePost($postData: PostInput!) {
      createPost(newPost: $postData) {
        ok
        post {
          id
          title
          slug
          content
          status
          author {
            username
          }
          category {
            name
          }
          tags {
            name
          }
        }
        errors {
          field
          messages
        }
      }
    }
    ```

=== "Variables"

    ```json
    {
      "postData": {
        "title": "Advanced GraphQL Techniques",
        "slug": "advanced-graphql-techniques",
        "content": "In this post, we'll explore advanced GraphQL patterns...",
        "excerpt": "Learn advanced GraphQL patterns and best practices",
        "status": "draft",
        "category": "1",
        "tags": ["1", "2", "3"]
      }
    }
    ```

### Updating Records

=== "Update Post"

    ```graphql
    mutation UpdatePost($postData: PostInput!) {
      updatePost(newPost: $postData) {
        ok
        post {
          id
          title
          content
          status
          updatedAt
        }
        errors {
          field
          messages
        }
      }
    }
    ```

=== "Variables"

    ```json
    {
      "postData": {
        "id": "1",
        "title": "Advanced GraphQL Techniques - Updated",
        "content": "Updated content with new examples...",
        "status": "published"
      }
    }
    ```

### File Uploads

=== "Update User Avatar"

    ```graphql
    mutation UpdateUserAvatar($userId: ID!, $avatar: Upload!) {
      updateUser(newUser: {id: $userId, profile: {avatar: $avatar}}) {
        ok
        user {
          id
          username
          profile {
            avatar
          }
        }
        errors {
          field
          messages
        }
      }
    }
    ```

### Error Handling

=== "Validation Error Example"

    ```json
    {
      "data": {
        "createPost": {
          "ok": false,
          "post": null,
          "errors": [
            {
              "field": "title",
              "messages": ["This field is required."]
            },
            {
              "field": "slug",
              "messages": ["Post with this slug already exists."]
            },
            {
              "field": "category",
              "messages": ["This field is required."]
            }
          ]
        }
      }
    }
    ```

## Using GraphQL Directives

### String Formatting

=== "Format Post Content"

    ```graphql
    query GetPostFormatted {
      post(id: "1") {
        title @uppercase
        excerpt @capitalize
        author {
          username @titleCase
          email @lowercase
        }
        content @strip
      }
    }
    ```

=== "Response"

    ```json
    {
      "data": {
        "post": {
          "title": "GETTING STARTED WITH GRAPHQL AND DJANGO",
          "excerpt": "Learn the basics of integrating graphql with django",
          "author": {
            "username": "John Doe",
            "email": "john@example.com"
          },
          "content": "GraphQL is a powerful query language for APIs..."
        }
      }
    }
    ```

### Number Formatting

=== "Format View Count"

    ```graphql
    query GetPostStats {
      posts(limit: 5) {
        id
        title
        viewCount @number(format: "en-US")
        createdAt @date(format: "YYYY-MM-DD")
      }
    }
    ```

=== "Response"

    ```json
    {
      "data": {
        "posts": [
          {
            "id": "1",
            "title": "Getting Started with GraphQL",
            "viewCount": "1,245",
            "createdAt": "2023-12-01"
          },
          {
            "id": "2",
            "title": "Advanced Django Techniques",
            "viewCount": "892",
            "createdAt": "2023-11-28"
          }
        ]
      }
    }
    ```

### Date Formatting

=== "Format Dates"

    ```graphql
    query GetPostDates {
      post(id: "1") {
        title
        createdAt @date(format: "MMMM DD, YYYY")
        publishedAt @date(format: "DD/MM/YYYY HH:mm")
        updatedAt @date(format: "relative")
      }
    }
    ```

## Frontend Integration Examples

### React with Apollo Client

=== "Posts List Component"

    ```javascript
    import React, { useState } from 'react';
    import { gql, useQuery } from '@apollo/client';

    const GET_POSTS = gql`
      query GetPosts(
        $limit: Int!,
        $offset: Int!,
        $search: String,
        $category: String,
        $status: String
      ) {
        allPosts(
          limit: $limit,
          offset: $offset,
          search: $search,
          category_Name: $category,
          status: $status,
          ordering: "-published_at"
        ) {
          results {
            id
            title
            excerpt
            publishedAt @date(format: "MMMM DD, YYYY")
            viewCount @number(format: "en-US")
            author {
              username
              profile {
                avatar
              }
            }
            category {
              name
              slug
            }
            tags {
              name
              color
            }
          }
          count
        }
      }
    `;

    function PostsList() {
      const [filters, setFilters] = useState({
        search: '',
        category: '',
        status: 'published'
      });
      const [pagination, setPagination] = useState({
        page: 0,
        limit: 10
      });

      const { loading, error, data, refetch } = useQuery(GET_POSTS, {
        variables: {
          ...filters,
          limit: pagination.limit,
          offset: pagination.page * pagination.limit
        }
      });

      const handleSearch = (searchTerm) => {
        setFilters(prev => ({ ...prev, search: searchTerm }));
        setPagination(prev => ({ ...prev, page: 0 }));
      };

      const handlePageChange = (newPage) => {
        setPagination(prev => ({ ...prev, page: newPage }));
      };

      if (loading) return <div>Loading posts...</div>;
      if (error) return <div>Error: {error.message}</div>;

      const posts = data?.allPosts?.results || [];
      const totalCount = data?.allPosts?.count || 0;
      const totalPages = Math.ceil(totalCount / pagination.limit);

      return (
        <div className="posts-list">
          {/* Search and Filters */}
          <div className="filters">
            <input
              type="text"
              placeholder="Search posts..."
              value={filters.search}
              onChange={(e) => handleSearch(e.target.value)}
            />
            <select
              value={filters.category}
              onChange={(e) => setFilters(prev => ({
                ...prev,
                category: e.target.value
              }))}
            >
              <option value="">All Categories</option>
              <option value="Technology">Technology</option>
              <option value="Design">Design</option>
            </select>
          </div>

          {/* Posts Grid */}
          <div className="posts-grid">
            {posts.map(post => (
              <article key={post.id} className="post-card">
                <h2>{post.title}</h2>
                <p>{post.excerpt}</p>
                <div className="post-meta">
                  <span>By {post.author.username}</span>
                  <span>{post.publishedAt}</span>
                  <span>{post.viewCount} views</span>
                </div>
                <div className="post-tags">
                  {post.tags.map(tag => (
                    <span
                      key={tag.name}
                      style={{ color: tag.color }}
                    >
                      #{tag.name}
                    </span>
                  ))}
                </div>
              </article>
            ))}
          </div>

          {/* Pagination */}
          <div className="pagination">
            <button
              disabled={pagination.page === 0}
              onClick={() => handlePageChange(pagination.page - 1)}
            >
              Previous
            </button>

            <span>
              Page {pagination.page + 1} of {totalPages}
            </span>

            <button
              disabled={pagination.page >= totalPages - 1}
              onClick={() => handlePageChange(pagination.page + 1)}
            >
              Next
            </button>
          </div>
        </div>
      );
    }

    export default PostsList;
    ```

=== "Create Post Form"

    ```javascript
    import React, { useState } from 'react';
    import { gql, useMutation, useQuery } from '@apollo/client';

    const CREATE_POST = gql`
      mutation CreatePost($postData: PostInput!) {
        createPost(newPost: $postData) {
          ok
          post {
            id
            title
            slug
            status
          }
          errors {
            field
            messages
          }
        }
      }
    `;

    const GET_CATEGORIES_AND_TAGS = gql`
      query GetCategoriesAndTags {
        categories {
          id
          name
        }
        tags {
          id
          name
          color
        }
      }
    `;

    function CreatePostForm() {
      const [formData, setFormData] = useState({
        title: '',
        slug: '',
        content: '',
        excerpt: '',
        status: 'draft',
        category: '',
        tags: []
      });

      const { data: optionsData } = useQuery(GET_CATEGORIES_AND_TAGS);
      const [createPost, { loading, error }] = useMutation(CREATE_POST);

      const handleSubmit = async (e) => {
        e.preventDefault();

        try {
          const result = await createPost({
            variables: { postData: formData }
          });

          if (result.data.createPost.ok) {
            alert('Post created successfully!');
            // Reset form or redirect
          } else {
            // Handle validation errors
            console.error('Validation errors:', result.data.createPost.errors);
          }
        } catch (err) {
          console.error('Mutation error:', err);
        }
      };

      return (
        <form onSubmit={handleSubmit} className="create-post-form">
          <div className="form-group">
            <label>Title</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                title: e.target.value,
                slug: e.target.value.toLowerCase().replace(/\s+/g, '-')
              }))}
              required
            />
          </div>

          <div className="form-group">
            <label>Slug</label>
            <input
              type="text"
              value={formData.slug}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                slug: e.target.value
              }))}
              required
            />
          </div>

          <div className="form-group">
            <label>Content</label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                content: e.target.value
              }))}
              rows={10}
              required
            />
          </div>

          <div className="form-group">
            <label>Category</label>
            <select
              value={formData.category}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                category: e.target.value
              }))}
              required
            >
              <option value="">Select Category</option>
              {optionsData?.categories?.map(category => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Status</label>
            <select
              value={formData.status}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                status: e.target.value
              }))}
            >
              <option value="draft">Draft</option>
              <option value="published">Published</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="submit-button"
          >
            {loading ? 'Creating...' : 'Create Post'}
          </button>

          {error && (
            <div className="error-message">
              Error: {error.message}
            </div>
          )}
        </form>
      );
    }

    export default CreatePostForm;
    ```

## Performance Tips

### Database Optimization

=== "Efficient Queries with select_related"

    ```python
    class PostListType(DjangoListObjectType):
        class Meta:
            model = Post
            pagination = LimitOffsetGraphqlPagination(default_limit=10)

        @classmethod
        def get_queryset(cls, queryset, info):
            return queryset.select_related(
                'author', 'author__profile', 'category'
            ).prefetch_related(
                'tags', 'comments__author'
            )
    ```

=== "Custom Resolver Optimization"

    ```python
    class Query(graphene.ObjectType):
        popular_posts = DjangoFilterListField(PostType)

        def resolve_popular_posts(self, info, **kwargs):
            return Post.objects.filter(
                status='published',
                view_count__gte=100
            ).select_related(
                'author', 'category'
            ).prefetch_related(
                'tags'
            ).order_by('-view_count')
    ```

These comprehensive examples demonstrate the full power of `graphene-django-extras` in building feature-rich GraphQL APIs with Django. The combination of filtering, pagination, mutations, and directives provides a robust foundation for modern web applications.
