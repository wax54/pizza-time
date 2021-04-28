from unittest import TestCase
from app import app
from db_setup import db
from users.models import User


# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///pizza_time_test'
app.config['SQLALCHEMY_ECHO'] = True

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False


user1_data = {"email": "test1@email.com",
              "token": "TESTTOKEN1", "name": "TESTUSER1"}
user2_data = {"email": "test2@email.com",
              "token": "TESTTOKEN2", "name": "TESTUSER2"}


class LoginTests(TestCase):
    def setUp(self):
        User.query.delete()
        db.session.commit()

    def test_create_or_update_creates_a_user(self):
        u_id = User.create_or_update(**user1_data)
        self.assertIsNotNone(u_id)
        user = User.query.get(u_id)
        self.assertEqual(user.name, user1_data["name"])
        self.assertEqual(user.token, user1_data["token"])
        self.assertEqual(user.email, user1_data["email"])

    def test_create_or_update_updates_a_user(self):
        u_id = User.create_or_update(**user1_data)

        anoter_u_id = User.create_or_update(
            email=user1_data['email'], token="SOMEOTHERTOKEN", name="A NICK NAME")
        #same email, same user id
        self.assertEqual(u_id, anoter_u_id)
        user = User.query.get(u_id)
        self.assertEqual(
            user.name, "A NICK NAME")
        self.assertEqual(
            user.token, "SOMEOTHERTOKEN")
        self.assertEqual(
            user.email, user1_data["email"])
