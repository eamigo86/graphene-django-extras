import factory

from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    # username = factory.Faker("user_name")
    username = "graphql"
    # first_name = factory.Faker("first_name")
    first_name = "Ernesto"
    # last_name = factory.Faker("last_name")
    last_name = "Perez Amigo"
    # email = factory.Faker("email")
    email = "eamigop86@gmail.com"

    class Meta:
        model = User
        django_get_or_create = ("username",)
