from django.test import TestCase
import factory
from graphene.utils.str_converters import to_camel_case

from tests import queries
from tests.client import Client
from tests.factories import BasicFactory, UserFactory
from tests.models import BasicModel
from tests.utils import query_builder


class BaseTest(TestCase):
    expected_status_code = 200

    def login(self):
        user = self.user
        self.client.login(username=user.username, password='password')

    def setUp(self):
        self.client = Client()
        self.user = UserFactory()

    def try_mutate(self, query, operation_name, variables):
        full_query = query % {
            "name": operation_name
        }

        payload = query_builder(
            full_query, operation_name,
            variables=variables
        )

        response = self.client.mutate(payload)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.status_code, self.expected_status_code)

        return response


class DRFBasicModelSerializerMutationTest(BaseTest):

    def test_can_create_basic_model(self):
        op_name = to_camel_case('create_basic_se')
        variables = {'text':  factory.Faker('sentence', nb_words=6).generate()}

        response = self.try_mutate(queries.create_mutation, op_name, variables)

        data = response.json()
        query_data = data['data'][op_name]
        self.assertTrue(query_data.get('ok'))

    def test_can_update_basic_model(self):
        basic_model_id = BasicFactory().id
        op_name = to_camel_case('update_basic_se')

        variables = {
            'id': basic_model_id,
            'text': f"update-text: {factory.Faker('sentence', nb_words=6).generate()}"
        }

        response = self.try_mutate(queries.update_mutation, op_name, variables)
        data = response.json()
        query_data = data['data'][op_name]
        self.assertTrue(query_data.get('ok'))

        self.assertIn('update-text', BasicModel.objects.get(id=basic_model_id).text)

    def test_can_delete_basic_model(self):
        basic_model_id = BasicFactory().id
        op_name = to_camel_case('delete_basic_se')

        variables = {
            'id': basic_model_id
        }

        response = self.try_mutate(queries.delete_mutation, op_name, variables)
        data = response.json()
        query_data = data['data'][op_name]

        self.assertTrue(query_data.get('ok'))
        self.assertIsNone(BasicModel.objects.filter(id=basic_model_id).first())


class DjangoBasicModelMutationTest(BaseTest):

    def test_anonymous_user_can_not_create_basic_model(self):
        op_name = to_camel_case('create_basic')
        variables = {'text':  factory.Faker('sentence', nb_words=6).generate()}

        response = self.try_mutate(queries.create_mutation, op_name, variables)

        data = response.json()
        query_data = data['errors']
        self.assertIsNotNone(query_data, 'Must have error(s)')

    def test_authenticated_user_can_create_basic_model(self):
        op_name = to_camel_case('create_basic')
        variables = {'text':  factory.Faker('sentence', nb_words=6).generate()}

        self.login()
        response = self.try_mutate(queries.create_mutation, op_name, variables)

        data = response.json()
        query_data = data['data'][op_name]
        self.assertTrue(query_data.get('ok'))

    def test_authenticated_user_can_update_basic_model(self):
        basic_model_id = BasicFactory().id
        op_name = to_camel_case('update_basic')

        variables = {
            'id': basic_model_id,
            'text': f"update-text: {factory.Faker('sentence', nb_words=6).generate()}"
        }

        self.login()
        response = self.try_mutate(queries.update_mutation, op_name, variables)

        data = response.json()
        query_data = data['data'][op_name]
        self.assertTrue(query_data.get('ok'))

        self.assertIn('update-text', BasicModel.objects.get(id=basic_model_id).text)

    def test_authenticated_user_can_delete_basic_model(self):
        basic_model_id = BasicFactory().id
        op_name = to_camel_case('delete_basic')

        variables = {
            'id': basic_model_id
        }
        self.login()
        response = self.try_mutate(queries.delete_mutation, op_name, variables)

        data = response.json()
        query_data = data['data'][op_name]

        self.assertTrue(query_data.get('ok'))
        self.assertIsNone(BasicModel.objects.filter(id=basic_model_id).first())