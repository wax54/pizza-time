from unittest import TestCase
from app import app
from db_setup import db
from users.models import User
from customers.models import Customer, Note
from config import USER_SESSION_KEY

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
cust2_data = {"id": '2',
              "name": "testuser2",
              "address": "The Eifel Tower",
              "phone": "872-164-2847"}


def seed_db():
    global test_driver_id
    global cust1_id
    global cust2_id
    global test_note_text

    db.drop_all()
    db.create_all()

    test_driver = User(email="test@email.com",
                       token="testToken", api_id='demo')
    cust1 = Customer(**cust1_data)
    cust2 = Customer(**cust2_data)

    db.session.add(cust1)
    db.session.add(cust2)
    db.session.add(test_driver)

    db.session.commit()
    test_note_text = "HELLO THERE!"
    note = Note(driver_id=test_driver.id,
                cust_id=cust1.id, note=test_note_text)
    db.session.add(note)
    db.session.commit()

    # variables to reference
    test_driver_id = test_driver.id
    cust1_id = cust1.id
    cust2_id = cust2.id
    test_note_text = test_note_text


class ViewCustomerTests (TestCase):
    @classmethod
    def setUpClass(cls):
        seed_db()

    def setUp(self):
        db.session.rollback()
        self.base_url = "http://localhost/customers"

    def test_get_returns_200(self):
        with app.test_client() as client:
            #log in user
            with client.session_transaction() as sess:
                sess[USER_SESSION_KEY] = test_driver_id

            res = client.get(f"{self.base_url}/{cust1_id}")
            self.assertEqual(res.status_code, 200)

    def test_customer_info_on_page(self):
        with app.test_client() as client:
            #log in user
            with client.session_transaction() as sess:
                sess[USER_SESSION_KEY] = test_driver_id
            customer = Customer.query.get(cust1_id)
            res = client.get(f"{self.base_url}/{cust1_id}")
            html = res.get_data(as_text=True)
            self.assertIn(customer.name, html)
            self.assertIn(customer.notes[0].note, html)
