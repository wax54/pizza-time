from unittest import TestCase
from api import pag_api

# NOTE THIS TEST WON'T WORK WITHOUT VALID PAGLIACCI DB CREDENTIALS LOCATED IN tests.api.pag_secrets.py
from tests.api.pag_secrets import working_email, working_password

print ('helo!')
class LoginTests(TestCase):

    def test_login_with_valid_creds_returns_valid_token(self):
        print('helo!')
        token = pag_api.login(
            email=working_email, password=working_password)
        print('helo!')
        self.assertTrue(token)
        result = pag_api.get_delivery(email=working_email, token=token)
        self.assertTrue(result)

    def test_login_with_invalid_creds_returns_false(self):
        token = pag_api.login(
            email=working_email, password="BADPASSWORD")
        self.assertFalse(token)

        token = pag_api.login(
            email="bad@email.com", password=working_password)
        self.assertFalse(token)

    def test_login_with_empty_creds_returns_false(self):
        token = pag_api.login(
            email="", password="")
        self.assertFalse(token)


class GetDeliveriesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.token = pag_api.login(
            email=working_email, password=working_password)

    def test_valid_credentals_returns_delivery(self):
        # NOTE delivery.orders may be just an empty list
        delivery = pag_api.get_delivery(email=working_email, token=self.token)
        self.assertIsInstance(delivery.get('orders'), list)



    def test_invalid_credentals_return_false(self):
        delivery = pag_api.get_delivery(email=working_email, token="badtoken")
        self.assertFalse(delivery)
        delivery = pag_api.get_delivery(
            email="bad@email.com", token=self.token)
        self.assertFalse(delivery)

    def test_empty_creds_return_false(self):
        delivery = pag_api.get_delivery(
            email="", token="")
        self.assertFalse(delivery)


class GetSchedulesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.token = pag_api.login(
            email=working_email, password=working_password)

    def test_valid_credentals_return_schedule(self):
        schedules = pag_api.get_schedules(
            email=working_email, token=self.token)

        self.assertIsInstance(schedules, list)

        # this assumes the user has a schedule already
        self.assertIsInstance(schedules[0].get('schedule'), list)
        self.assertIsNotNone(schedules[0].get('pag_code'))

    def test_invalid_credentals_return_false(self):
        schedules = pag_api.get_schedules(
            email=working_email, token="badtoken")
        self.assertFalse(schedules)
        schedules = pag_api.get_schedules(
            email="bad@email.com", token=self.token)
        self.assertFalse(schedules)

    def test_does_not_return_weeks_in_ignore_list(self):
        schedules = pag_api.get_schedules(
            email=working_email, token=self.token)
        week_codes = [week['pag_code'] for week in schedules]

        empty_schedules = pag_api.get_schedules(
            email=working_email, token=self.token, ignore=week_codes)
        self.assertEqual(empty_schedules, [])
