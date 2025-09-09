from django.contrib.auth import models as auth_models

from rest_framework import serializers

from .models import BasicModel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = auth_models.User
        fields = ["id", "username", "email", "first_name", "last_name", "password"]
        extra_kwargs = {"password": {"write_only": True}}


class BasicModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicModel
        fields = ["id", "text"]
