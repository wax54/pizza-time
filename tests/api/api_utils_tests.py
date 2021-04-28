from unittest import TestCase
from api.utils import *
from datetime import date as date_class


class GetDateTests(TestCase):
    def setUp(self):
        self.test_date_string = "Mon, 19 Apr 2021 00:00:00 GMT"

    def test_get_date_returns_date(self):
        date = get_date(self.test_date_string)
        self.assertIsInstance(date, date_class)
