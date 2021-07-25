from unittest import TestCase
from api import demo_api


class LoginTests(TestCase):

    def test_login_with_creds_returns_valid_token(self):
        demo_email = "AnyString"
        demo_password = "LiterlyAnyStringShouldWork"
        token = demo_api.login(
            email=demo_email, password=demo_password)
        self.assertTrue(token)
        result = demo_api.get_delivery(email=demo_email, token=token)
        self.assertTrue(result)

    def test_login_with_no_creds_returns_valid_token(self):

        demo_email = "AnyString"
        token = demo_api.login()
        self.assertTrue(token)
        result = demo_api.get_delivery(email=demo_email, token=token)
        self.assertTrue(result)


class GetDeliveriesTests(TestCase):

    def setUp(self):
        self.email = "AnyString"
        self.token = "AnotherString"

    def test_any_credentals_returns_delivery(self):
        delivery = demo_api.get_delivery(email=self.email, token=self.token)
        self.assertIsInstance(delivery.get('orders'), list)
        self.assertEqual(delivery, demo_api.DEMO_DELIVERY)

    def test_empty_creds_return_false(self):
        delivery = demo_api.get_delivery(
            email="", token=self.token)
        self.assertFalse(delivery)

        delivery = demo_api.get_delivery(
            email=self.email, token="")
        self.assertFalse(delivery)

        delivery = demo_api.get_delivery(
            email="", token="")
        self.assertFalse(delivery)


class GetSchedulesTests(TestCase):
    def setUp(self):
        self.email = "AnyString"
        self.token = "AnotherString"

    def test_any_credentals_returns_schedules(self):
        schedules = demo_api.get_schedules(email=self.email, token=self.token)
        self.assertIsInstance(schedules, list)
        self.assertEqual(schedules, demo_api.DEMO_SCHEDULES)

    def test_empty_creds_return_false(self):
        schedules = demo_api.get_schedules(
            email="", token=self.token)
        self.assertFalse(schedules)

        schedules = demo_api.get_schedules(
            email=self.email, token="")
        self.assertFalse(schedules)

        schedules = demo_api.get_schedules(
            email="", token="")
        self.assertFalse(schedules)

    def test_does_not_return_weeks_in_ignore_list(self):
        schedules = demo_api.get_schedules(
            email=self.email, token=self.token)
        week_codes = [week['week_code'] for week in schedules]

        empty_schedules = demo_api.get_schedules(
            email=self.email, token=self.token, ignore=week_codes)
        self.assertEqual(empty_schedules, [])
