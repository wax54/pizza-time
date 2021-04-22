from unittest import TestCase
from app import app
from db_setup import db
from users.models import User
import api.pag_api as api
from config import USER_KEY

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///pag_api_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()

working_email = "wax654@gmail.com"
working_password = "Pizza11"


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
                sess[USER_KEY] = self.user_id
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
                '/login', data={'email': "testEmail", "password": "testPassword1"})
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)

            self.assertIn('Not Valid Credentials!', html)
            self.assertIn('<form method="POST" id="login_form">', html)
            self.assertIn('testEmail', html)

    def test_post_redirects_on_success(self):

        with app.test_client() as client:
            res = client.post(
                '/login', data={'email': working_email, "password": working_password})

            self.assertEqual(res.status_code, 302)
            self.assertEqual(
                res.location, "http://localhost/pag/current_delivery")

            user = User.query.filter_by(email=working_email).first()
            self.assertIsNotNone(user)
