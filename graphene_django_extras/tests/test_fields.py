from django.test import TestCase
from graphene_django_extras.tests.client import Client
from graphene_django_extras.tests import factories


query = '''query {
  allUsers {
    results {
      id
    }
  }
}
'''
class DjangoListObjectFieldTest(TestCase):
    def test_foo(self):
        user = factories.UserFactory()
        client = Client()
        response = client.query(query)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('data', data)
        self.assertIn('allUsers', data['data'])
        self.assertIn('results', data['data']['allUsers'])
        self.assertTrue(data['data']['allUsers'])
