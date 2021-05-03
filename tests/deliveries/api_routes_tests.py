from flask import session
from unittest import TestCase
from app import app
from config import USER_SESSION_KEY
from db_setup import db

from deliveries.models import *

from users.models import User


# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///pizza_time_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False


cust1_data = {"id": '1',
              "name": "testuser1",
              "address": "Some Address",
              "phone": "203-881-7843"}


def seed_db():
    global test_driver_id
    global cust1_id

    db.session.rollback()

    db.drop_all()
    db.create_all()

    test_driver = User(email="test@email.com", token="testToken", api_id="demo")
    cust1 = Customer(**cust1_data)

    db.session.add(cust1)
    db.session.add(test_driver)

    db.session.commit()

    # global variables
    test_driver_id = test_driver.id
    cust1_id = cust1.id


class UpdateOrderTipTests(TestCase):
    @classmethod
    def setUpClass(cls):
        seed_db()

    def setUp(self):
        db.session.rollback()
        self.url = '/edit_order_tip'

    def test_tip_changes_in_db(self):
        new_tip = 5
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[USER_SESSION_KEY] = test_driver_id
            res = client.post(self.url, json={
                'customer_id': cust1_id,
                'note': test_note_text
            })

            note = Note.query.filter_by(note=test_note_text).first()

            self.assertEqual(note.note, test_note_text)
            self.assertEqual(note.driver_id, test_driver_id)
            self.assertEqual(note.cust_id, cust1_id)

    def test_response_with_correct_input(self):
        test_note_text = "TEST NOTE!"
        with app.test_client() as client:
            #log in user
            with client.session_transaction() as sess:
                sess[USER_SESSION_KEY] = test_driver_id

            res = client.post(self.url, json={
                'customer_id': cust1_id,
                'note': test_note_text
            })
            json = res.json
            self.assertTrue(json['status'])

            self.assertEqual(json['note']['note'], test_note_text)
            self.assertEqual(json['note']['driver_id'], test_driver_id)
            self.assertEqual(json['note']['cust_id'], cust1_id)

    def test_user_must_be_logged_in_to_use(self):
        test_note_text = "TEST NOTE!"
        with app.test_client() as client:
            res = client.post(self.url, json={
                'customer_id': cust1_id,
                'note': test_note_text
            })
            self.assertFalse(res.json['status'])
            self.assertEqual(res.json['message'], 'Not Logged In')

    def test_what_happens_if_no_json(self):
        with app.test_client() as client:
            #log in user
            with client.session_transaction() as sess:
                sess[USER_SESSION_KEY] = test_driver_id
            # no json at all
            res = client.post(self.url)
            json = res.json
            self.assertFalse(res.json['status'])
            self.assertEqual(res.json['message'], "POST missing JSON")
            # empty json
            res = client.post(self.url, json={})
            json = res.json
            self.assertFalse(res.json['status'])
            self.assertEqual(res.json['message'], "POST missing JSON")

    def test_missing_inputs(self):
        test_note_text = "TEST NOTE!"
        with app.test_client() as client:
            #log in user
            with client.session_transaction() as sess:
                sess[USER_SESSION_KEY] = test_driver_id

            # with json inputs, just not the right ones
            res = client.post(self.url, json={"garbage": "garbage Input"})
            json = res.json
            self.assertFalse(res.json['status'])
            self.assertEqual(
                res.json['message'],
                "missing customer_id or new_note from json POST")
            # with missing json inputs
            res = client.post(self.url, json={
                'note': test_note_text
            })
            json = res.json
            self.assertFalse(res.json['status'])
            self.assertEqual(
                res.json['message'],
                "missing customer_id or new_note from json POST")
            # prove the note didn't get stored
            note = Note.query.filter_by(note=test_note_text).first()
            self.assertIsNone(note)

            res = client.post(self.url, json={
                'customer_id': cust1_id
            })
            json = res.json
            self.assertFalse(res.json['status'])
            self.assertEqual(
                res.json['message'],
                "missing customer_id or new_note from json POST")

    def test_empty_string_inputs(self):
        test_note_text = "TEST NOTE!"
        with app.test_client() as client:
            #log in user
            with client.session_transaction() as sess:
                sess[USER_SESSION_KEY] = test_driver_id

            res = client.post(self.url, json={
                'customer_id': "",
                'note': test_note_text
            })
            json = res.json
            self.assertFalse(res.json['status'])
            self.assertEqual(
                res.json['message'],
                "missing customer_id or new_note from json POST")

            # prove the note didn't get stored in the DB
            note = Note.query.filter_by(note=test_note_text).first()
            self.assertIsNone(note)

            res = client.post(self.url, json={
                'customer_id': cust1_id,
                'note': ""
            })
            json = res.json
            self.assertFalse(res.json['status'])
            self.assertEqual(
                res.json['message'],
                "missing customer_id or new_note from json POST")

            # prove the note didn't get stored in the DB
            note = Note.query.filter_by(note=test_note_text).first()
            self.assertIsNone(note)

    def test_invalid_inputs(self):
        test_note_text = "TEST NOTE!"
        with app.test_client() as client:
            #log in user
            with client.session_transaction() as sess:
                sess[USER_SESSION_KEY] = test_driver_id

            res = client.post(self.url, json={
                'customer_id': "GarbageInput",
                'note': test_note_text
            })
            json = res.json
            self.assertFalse(res.json['status'])
            self.assertEqual(
                res.json['message'],
                "There was an error entering your data, please check it and try again.")

            # prove the note didn't get stored in the DB
            note = Note.query.filter_by(note=test_note_text).first()
            self.assertIsNone(note)

    def test_new_tip_is_has_no_change(self):
        test_note_text = "TEST NOTE!"
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[USER_SESSION_KEY] = test_driver_id
            res = client.post(self.url, json={
                'customer_id': cust1_id,
                'note': test_note_text
            })
            self.assertTrue(res.json['status'])

            res = client.post(self.url, json={
                'customer_id': cust1_id,
                'note': test_note_text
            })
            note = res.json['note']
            self.assertEqual(note['note'], test_note_text)
            self.assertEqual(note['driver_id'], test_driver_id)
            self.assertEqual(note['cust_id'], cust1_id)
