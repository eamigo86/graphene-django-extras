from django.test import TestCase
from graphene.utils.str_converters import to_camel_case
from graphql_relay import to_global_id

from tests import queries
from tests.factories import BasicFactory
from tests.mutations import BasicModelNodeType
from tests.test_fields import ParentTest


class BaseTest(ParentTest):

    @property
    def query(self):
        raise NotImplementedError()

    def login(self):
        user = self.user
        self.client.login(username=user.username, password='password')


class RetrieveFieldTest(BaseTest, TestCase):
    op_name = to_camel_case("retrieve_basic_model_id")
    expected_return_payload = {
        "data": {op_name: {"text": "Some text", "id": str(1)}}
    }

    @property
    def query(self):
        self.login()
        basic_model = BasicFactory(text='Some text')
        return queries.generic_query % {
            "params": "id: %s" % basic_model.id,
            "name": self.op_name,
            "fields": "text id"
        }


class DjangoNodeFieldTest(BaseTest, TestCase):
    op_name = to_camel_case("get_basic_model_id")
    expected_return_payload = {
        "data": {op_name: {"text": "Some text", "id": to_global_id(BasicModelNodeType.__name__, 1)}}
    }

    def setUp(self):
        super(DjangoNodeFieldTest, self).setUp()

    @property
    def query(self):
        self.login()
        model = BasicFactory(text='Some text')
        return queries.generic_query % {
            "params": 'id: "%s"' % to_global_id(BasicModelNodeType.__name__, model.id),
            "name": self.op_name,
            "fields": "text id"
        }
