from django.test import TestCase
from graphene_django_extras.tests.client import Client
from graphene_django_extras.tests import factories
from graphene_django_extras.tests import queries


class DjangoListObjectFieldTest(TestCase):
    def test_field(self):
        user = factories.UserFactory()
        client = Client()
        response = client.query(queries.ALL_USERS)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('data', data)
        self.assertIn('allUsers', data['data'])
        self.assertIn('results', data['data']['allUsers'])
        self.assertTrue(data['data']['allUsers']['results'])
        self.assertEqual(data['data']['allUsers']['results'][0]['id'], str(user.id))


class DjangoFilterPaginateListFieldTest(TestCase):
    def test_field(self):
        user = factories.UserFactory()
        client = Client()
        response = client.query(queries.ALL_USERS1)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('data', data)
        self.assertIn('allUsers1', data['data'])
        self.assertIn('results', data['data']['allUsers1'])
        self.assertTrue(data['data']['allUsers1'])
        self.assertEqual(data['data']['allUsers1'][0]['id'], str(user.id))


class DjangoFilterListFieldTest(TestCase):
    def test_field(self):
        user = factories.UserFactory()
        client = Client()
        response = client.query(queries.ALL_USERS2)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('allUsers2', data['data'])
        self.assertTrue(data['data']['allUsers2'])
        self.assertEqual(data['data']['allUsers2'][0]['id'], str(user.id))


class DjangoListObjectFieldWithFiltersetTest(TestCase):
    def test_filter_id(self):
        user = factories.UserFactory()
        query = queries.ALL_USERS3_WITH_FILTER % {
            'filter': 'id: %s' % user.id,
            'fields': 'username',
        }
        client = Client()
        response = client.query(query)
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertIn('allUsers3', data['data'])
        self.assertIn('results', data['data']['allUsers3'])
        self.assertTrue(data['data']['allUsers3']['results'])
        self.assertEqual(data['data']['allUsers3']['results'][0]['username'], user.username)

    def test_filter_charfield_icontains(self):
        user = factories.UserFactory()
        query = queries.ALL_USERS3_WITH_FILTER % {
            'filter': 'email_Icontains: "%s"' % user.email.split('@')[0],
            'fields': 'username',
        }
        client = Client()
        response = client.query(query)
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertIn('allUsers3', data['data'])
        self.assertIn('results', data['data']['allUsers3'])
        self.assertTrue(data['data']['allUsers3']['results'])
        self.assertEqual(data['data']['allUsers3']['results'][0]['username'], user.username)

    def test_filter_charfield_iexact(self):
        user = factories.UserFactory()
        query = queries.ALL_USERS3_WITH_FILTER % {
            'filter': 'email_Iexact: "%s"' % user.email,
            'fields': 'username',
        }
        client = Client()
        response = client.query(query)
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertIn('allUsers3', data['data'])
        self.assertIn('results', data['data']['allUsers3'])
        self.assertTrue(data['data']['allUsers3']['results'])
        self.assertEqual(data['data']['allUsers3']['results'][0]['username'], user.username)
