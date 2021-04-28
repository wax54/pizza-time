
# NOTE THIS TEST WON'T WORK WITHOUT VALID PAGLIACCI DB CREDENTIALS LOCATED IN tests.api.pag_secrets.py
from tests.api.pag_secrets import working_email, working_password
from unittest import TestCase
from app import app
from db_setup import db
from users.models import User
from api import PAG_KEY as PAG_API_KEY, DEMO_KEY as DEMO_API_KEY
import api.pag_api as api
from config import USER_SESSION_KEY

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///pizza_time_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()


class GetDeliveryTests(TestCase):
    def setUp(self):
        token = api.login(email=working_email, password=working_password)
        self.user_id = User.create_or_update(email=working_email, token=token)

    def test_redirects_if_not_logged_in(self):
        with app.test_client() as client:
            res = client.get('/pag/current_delivery')
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, 'http://localhost/login')

    def test_shows_page_if_logged_in(self):
        with app.test_client() as client:
            # Set logged in
            with client.session_transaction() as sess:
                sess[USER_SESSION_KEY] = self.user_id
            res = client.get('/pag/current_delivery')
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            self.assertIn(
                f"Hello {working_email}, Good to see you again!", html)


class LoginTests(TestCase):
    def test_get_gets_page(self):
        with app.test_client() as client:
            res = client.get('/login')
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            self.assertIn('<form method="POST" id="login_form">', html)

    def test_post_returns_page_on_bad_creds(self):
        with app.test_client() as client:
            res = client.post(
                '/login', data={'email': "testEmail", "password": "testPassword1", "api": PAG__API_KEY})
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)

            self.assertIn('Not Valid Credentials!', html)
            self.assertIn('<form method="POST" id="login_form">', html)
            self.assertIn('testEmail', html)

    def test_post_redirects_on_success(self):

        with app.test_client() as client:
            res = client.post(
                '/login', data={'email': "super@roo.com", "password": "password", "api": DEMO__API_KEY})

            self.assertEqual(res.status_code, 302)
            self.assertEqual(
                res.location, "http://localhost/pag/current_delivery")

            user = User.query.filter_by(email=working_email).first()
            self.assertIsNotNone(user)
