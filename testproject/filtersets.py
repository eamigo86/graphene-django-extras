from django.contrib.auth import models as auth_models
import django_filters as filters


class UserFilter(filters.FilterSet):
    class Meta:
        model = auth_models.User
        fields = '__all__'
