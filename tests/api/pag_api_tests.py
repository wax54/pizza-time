from unittest import TestCase, mock
from api import pag_api, utils

VALID_EMAIL = "test@test.com"
VALID_PASSWORD = "SecretPassword"
VALID_TOKEN = "PAG_TOKEN"

class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

class MockSession:
    def get(self, *args, **kwargs): 
        if args[0] == 'https://www.sam-the-dev.com/pag_api/users/get_delivery':
            json = kwargs['json']
            return mock_pag_delivery_route(json)
        else:
            return MockResponse(None, 404)
        

    def post(self, *args, **kwargs):
        if args[0] == 'https://www.sam-the-dev.com/pag_api/login':
            json = kwargs['json']
            return mock_pag_login_route(json)
        else:
            return MockResponse(None, 404)

    def close(self):
        pass

def mock_pag_login_route(json):
    if json['email'] == VALID_EMAIL and json['password'] == VALID_PASSWORD:
        return MockResponse({"status": True, "user": {"token": VALID_TOKEN, "expiration": "Mon, 19 Apr 2021 00:00:00 GMT"}}, 200)
    else:
        return MockResponse({"status": False}, 200)


def mock_pag_delivery_route(json):
    if json['email'] == VALID_EMAIL and json['token'] == VALID_TOKEN:
        return MockResponse({"status": True, "delivery": {"date": "Mon, 19 Apr 2021 00:00:00 GMT", "orders" : []}}, 200)
    else:
        return MockResponse({"status": False}, 200)

# This method will be used by the mock to replace session with a mock session
def mocked_request_with_retry(*args, **kwargs):
    return MockSession()



class LoginTests(TestCase):
    # We patch 'request_with_retry' with our own one that returns the mock session object
    @mock.patch('api.pag_api.request_with_retry', side_effect=mocked_request_with_retry)
    def test_login_with_valid_creds_returns_valid_token(self, mock_session_getter):
        
        res = pag_api.login(
            email=VALID_EMAIL, password=VALID_PASSWORD)
        token = res['token']
        self.assertEqual(token, VALID_TOKEN)
        
        result = pag_api.get_delivery(email=VALID_EMAIL, token=token)
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


# class GetDeliveriesTests(TestCase):

#     @classmethod
#     def setUpClass(cls):
#         cls.token = pag_api.login(
#             email=working_email, password=working_password)

#     def test_valid_credentals_returns_delivery(self):
#         # NOTE delivery.orders may be just an empty list
#         delivery = pag_api.get_delivery(email=working_email, token=self.token)
#         self.assertIsInstance(delivery.get('orders'), list)



#     def test_invalid_credentals_return_false(self):
#         delivery = pag_api.get_delivery(email=working_email, token="badtoken")
#         self.assertFalse(delivery)
#         delivery = pag_api.get_delivery(
#             email="bad@email.com", token=self.token)
#         self.assertFalse(delivery)

#     def test_empty_creds_return_false(self):
#         delivery = pag_api.get_delivery(
#             email="", token="")
#         self.assertFalse(delivery)


# class GetSchedulesTests(TestCase):

#     @classmethod
#     def setUpClass(cls):
#         cls.token = pag_api.login(
#             email=working_email, password=working_password)

#     def test_valid_credentals_return_schedule(self):
#         schedules = pag_api.get_schedules(
#             email=working_email, token=self.token)

#         self.assertIsInstance(schedules, list)

#         # this assumes the user has a schedule already
#         self.assertIsInstance(schedules[0].get('schedule'), list)
#         self.assertIsNotNone(schedules[0].get('pag_code'))

#     def test_invalid_credentals_return_false(self):
#         schedules = pag_api.get_schedules(
#             email=working_email, token="badtoken")
#         self.assertFalse(schedules)
#         schedules = pag_api.get_schedules(
#             email="bad@email.com", token=self.token)
#         self.assertFalse(schedules)

#     def test_does_not_return_weeks_in_ignore_list(self):
#         schedules = pag_api.get_schedules(
#             email=working_email, token=self.token)
#         week_codes = [week['pag_code'] for week in schedules]

#         empty_schedules = pag_api.get_schedules(
#             email=working_email, token=self.token, ignore=week_codes)
#         self.assertEqual(empty_schedules, [])
