from django.test import TestCase

from tests.test_fields import ParentTest


class DateDirective_DateTime_Test(ParentTest, TestCase):
    query = """query { datetime @date(format:"HH:mm:ss YYYY.MM.DD") }"""
    expected_return_payload = {"data": {"datetime": "10:21:30 2020.12.31"}}


class DateDirective_Time_Test(ParentTest, TestCase):
    query = """query { time @date(format:"HH:mm:ss") }"""
    expected_return_payload = {"data": {"time": "10:21:30"}}


class DateDirective_Date_Test(ParentTest, TestCase):
    query = """query { date @date(format:"YYYY.MM.DD") }"""
    expected_return_payload = {"data": {"date": "2020.12.31"}}
