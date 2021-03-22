from django.test import TestCase
from tests import factories
from tests import queries
from tests.client import Client


class ParentTest:
    expected_status_code = 200
    expected_return_payload = {}

    @property
    def query(self):
        raise NotImplementedError()

    def setUp(self):
        self.user = factories.UserFactory()
        self.client = Client()
        self.response = self.client.query(self.query)
        self.data = self.response.json()

    def test_should_return_expected_status_code(self):
        self.assertEqual(self.response.status_code, self.expected_status_code)

    def test_should_return_expected_payload(self):
        self.assertEqual(
            self.response.json(), self.expected_return_payload, self.response.content
        )


class DjangoListObjectFieldTest(ParentTest, TestCase):
    query = queries.ALL_USERS
    expected_return_payload = {"data": {"allUsers": {"results": [{"id": "1"}]}}}

    def test_field(self):
        self.assertEqual(
            self.data["data"]["allUsers"]["results"][0]["id"], str(self.user.id)
        )


class DjangoFilterPaginateListFieldTest(ParentTest, TestCase):
    query = queries.ALL_USERS1
    expected_return_payload = {
        "data": {
            "allUsers1": [
                {
                    "id": "1",
                    "username": "graphql",
                    "firstName": "Ernesto",
                    "lastName": "Perez Amigo",
                    "email": "eamigop86@gmail.com",
                }
            ]
        }
    }


class DjangoFilterListFieldTest(ParentTest, TestCase):
    query = queries.ALL_USERS2
    expected_return_payload = {"data": {"allUsers2": [{"username": "graphql"}]}}


class DjangoListObjectFieldWithFilterSetTest(ParentTest, TestCase):
    expected_return_payload = {
        "data": {"allUsers3": {"results": [{"username": "graphql"}]}}
    }

    @property
    def query(self):
        return queries.ALL_USERS3_WITH_FILTER % {
            "filter": "id: %s" % self.user.id,
            "fields": "username",
        }

    def test_filter_charfield_icontains(self):
        query = queries.ALL_USERS3_WITH_FILTER % {
            "filter": 'email_Icontains: "%s"' % self.user.email.split("@")[0],
            "fields": "username",
        }
        response = self.client.query(query)
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertIn("allUsers3", data["data"])
        self.assertIn("results", data["data"]["allUsers3"])
        self.assertTrue(data["data"]["allUsers3"]["results"])
        self.assertEqual(
            data["data"]["allUsers3"]["results"][0]["username"], self.user.username
        )

    def test_filter_charfield_iexact(self):
        query = queries.ALL_USERS3_WITH_FILTER % {
            "filter": 'email_Iexact: "%s"' % self.user.email,
            "fields": "username",
        }
        response = self.client.query(query)
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertIn("allUsers3", data["data"])
        self.assertIn("results", data["data"]["allUsers3"])
        self.assertTrue(data["data"]["allUsers3"]["results"])
        self.assertEqual(
            data["data"]["allUsers3"]["results"][0]["username"], self.user.username
        )


class DjangoSerializerTypeTest(ParentTest, TestCase):
    expected_return_payload = {
        "data": {
            "users": {
                "results": [
                    {"id": "1", "username": "graphql", "email": "eamigop86@gmail.com"}
                ],
                "totalCount": 1,
            }
        }
    }

    @property
    def query(self):
        return queries.USERS % {
            "filter": 'firstName_Icontains: "{}"'.format(self.user.first_name[:5]),
            "pagination": "limit: 1",
            "fields": "id, username, email",
        }

    def test_filter_single_object(self):
        query = queries.USER % {
            "filter": "id: {}".format(self.user.id),
            "fields": "username",
        }
        response = self.client.query(query)
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertIn("user2", data["data"])
        self.assertTrue(data["data"]["user2"])
        self.assertEqual(data["data"]["user2"]["username"], self.user.username)
