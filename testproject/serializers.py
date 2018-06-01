from django.contrib.auth import models as auth_models
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = auth_models.User
