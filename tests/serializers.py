from django.contrib.auth import models as auth_models
from rest_framework import serializers

from tests.models import BasicModel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = auth_models.User


class BasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicModel
        fields = '__all__'

