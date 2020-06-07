import factory

from django.contrib.auth.models import User
from factory import post_generation

from tests.models import BasicModel


class UserFactory(factory.django.DjangoModelFactory):
    # username = factory.Faker("user_name")
    username = "graphql"
    # first_name = factory.Faker("first_name")
    first_name = "Ernesto"
    # last_name = factory.Faker("last_name")
    last_name = "Perez Amigo"
    # email = factory.Faker("email")
    email = "eamigop86@gmail.com"

    @post_generation
    def password(self, create, extracted, **kwargs):
        if create:
            self.set_password('password')

    class Meta:
        model = User
        django_get_or_create = ("username",)


class BasicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BasicModel

    text = factory.Faker('sentence', nb_words=10)
