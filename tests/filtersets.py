from django.contrib.auth import models as auth_models

import django_filters as filters


class UserFilterSet(filters.FilterSet):
    class Meta:
        model = auth_models.User
        fields = {
            "id": ("exact",),
            "first_name": ("icontains", "iexact"),
            "last_name": ("icontains", "iexact"),
            "username": ("icontains", "iexact"),
            "email": ("icontains", "iexact"),
            "is_staff": ("exact",),
        }
