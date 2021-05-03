from config import USER_SESSION_KEY, API_SESSION_KEY
from api import PAG_KEY as PAG_API_KEY, DEMO_KEY as DEMO_API_KEY
from users.models import User
from db_setup import db
from app import app
from unittest import TestCase


# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///pizza_time_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
user_data = {
    "name": "JERRY TEST",
    "email": "test@email.com",
    "token": "testToken", 
    "api_id" : 'demo'
}


def seed_the_db():
    global user_id
    db.session.rollback()
    db.drop_all()
    db.create_all()

    test_user = User(**user_data)

    db.session.add(test_user)

    db.session.commit()

    # variables to reference
    user_id = test_user.id


class GetDeliveryTests(TestCase):
    def setUp(self):
        seed_the_db()
        self.url = '/current_delivery'

    def test_redirects_if_not_logged_in(self):
        with app.test_client() as client:
            res = client.get(self.url)
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, 'http://localhost/login')

    def test_shows_page_if_logged_in(self):
        with app.test_client() as client:
            # Set logged in
            with client.session_transaction() as sess:
                sess[USER_SESSION_KEY] = user_id
                sess[API_SESSION_KEY] = DEMO_API_KEY
            res = client.get(self.url)
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            self.assertIn(
                f"Your Current Delivery!", html)


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
                '/login', data={'email': "testEmail", "password": "testPassword1", "api": PAG_API_KEY})
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)

            self.assertIn('Not Valid Credentials!', html)
            self.assertIn('<form method="POST" id="login_form">', html)
            self.assertIn('testEmail', html)

    def test_post_redirects_on_success(self):

        with app.test_client() as client:
            res = client.post(
                '/login', data={'email': "super@roo.com", "password": "password", "api": DEMO_API_KEY})

            self.assertEqual(res.status_code, 302)
            self.assertEqual(
                res.location, "http://localhost/current_delivery")

            user = User.query.filter_by(email="super@roo.com").first()
            self.assertIsNotNone(user)
