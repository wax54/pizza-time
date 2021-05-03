from unittest import TestCase
from app import app
from db_setup import db

from customers.models import *

from users.models import User
from customers.models import Note


# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///pizza_time_test'
app.config['SQLALCHEMY_ECHO'] = False


cust1_data = {"id": '1',
              "name": "testuser1",
              "address": "Some Address",
              "phone": "203-881-7843"}
cust2_data = {"id": '2',
              "name": "testuser2",
              "address": "The Eifel Tower",
              "phone": "872-164-2847"}


def seed_db():


    db.session.rollback()
    global test_driver_id
    global cust1_id
    global cust2_id
    # db.drop_all()
    # db.create_all()
    Customer.query.delete()
    User.query.delete()
    Note.query.delete()
    
    db.session.commit()

    test_driver = User(email="test@email.com",
                       token="testToken", api_id='demo')
    cust1 = Customer(**cust1_data)
    cust2 = Customer(**cust2_data)

    db.session.add(cust1)
    db.session.add(cust2)
    db.session.add(test_driver)

    db.session.commit()

    test_driver_id = test_driver.id
    cust1_id = cust1.id
    cust2_id = cust2.id




class NoteTests(TestCase):
    @classmethod
    def setUpClass(cls):
        seed_db()

    
    def setUp(self):
        Note.query.delete()

        self.note_text = "TEST_NOTE_TEXT"

        note = Note(driver_id=test_driver_id,
                    cust_id=cust1_id,
                    note=self.note_text)
        db.session.add(note)
        db.session.commit()

    def test_note_has_expected_params(self):
        note = Note.query.filter_by(note=self.note_text).first()

        self.assertEqual(note.driver_id, test_driver_id)
        self.assertEqual(note.cust_id, cust1_id)
        self.assertEqual(note.note, self.note_text)

        self.assertEqual(note.customer.id, cust1_id)
        self.assertEqual(note.driver.id, test_driver_id)

    def test_serialize_has_expected_params(self):
        note = Note.query.filter_by(note=self.note_text).first()
        note_serial = note.serialize()
        self.assertEqual(note_serial['driver_id'], test_driver_id)
        self.assertEqual(note_serial['cust_id'], cust1_id)
        self.assertEqual(note_serial['note'], self.note_text)

    def test_get(self):
        note = Note.get(cust_id=cust1_id, driver_id=test_driver_id)
        self.assertEqual(note.note, self.note_text)

        bogus_note = Note.get(cust_id='nonId', driver_id=test_driver_id)
        self.assertIsNone(bogus_note)

    def test_delete(self):
        note = Note.query.filter_by(note=self.note_text).first()
        # the Note Exists!
        self.assertIsNotNone(note)
        Note.delete(cust_id=cust1_id, driver_id=test_driver_id)

    def test_create_or_update_creates_a_note(self):

        new_note_text = "NEW TEST TEXT"
        # No note of this name exists in the Notes table
        test_note = Note.query.filter_by(note=new_note_text).first()
        self.assertIsNone(test_note)

        note = Note.create_or_update_note(
            cust_id=cust2_id,
            driver_id=test_driver_id,
            new_note=new_note_text)

        self.assertEqual(note.note, new_note_text)
        # now when we seach for it, it's there!
        test_note = Note.query.filter_by(note=new_note_text).first()
        self.assertIsNotNone(test_note)

    def test_create_or_update_updates_a_note(self):
        new_note_text = "NEW TEST TEXT"
        old_note = Note.query.filter_by(note=self.note_text).first()
        self.assertEqual(old_note.note, self.note_text)

        note = Note.create_or_update_note(
            cust_id=old_note.cust_id,
            driver_id=old_note.driver_id,
            new_note=new_note_text)

        self.assertEqual(note.note, new_note_text)
        # when we search for the note text in the DB, it is gone
        test_note = Note.query.filter_by(note=self.note_text).first()
        self.assertIsNone(test_note)


class CustomerTests(TestCase):
        
    def setUp(self):
        seed_db()
        self.cust1_note_text = "TEST_NOTE_TEXT"

        Note.query.delete()

        note = Note(driver_id=test_driver_id,
                    cust_id=cust1_id,
                    note=self.cust1_note_text)
        db.session.add(note)
        db.session.commit()

    def test_customer_has_expected_params(self):
        customer = Customer.query.get(cust1_id)

        self.assertEqual(customer.id, cust1_data['id'])
        self.assertEqual(customer.name, cust1_data['name'])
        self.assertEqual(customer.phone, cust1_data['phone'])
        self.assertEqual(customer.address, cust1_data['address'])

        self.assertIsInstance(customer.notes, list)
        self.assertEqual(customer.notes[0].note, self.cust1_note_text)

        self.assertIsInstance(customer.orders, list)

    def test_serialize_has_expected_params(self):
        customer = Customer.query.get(cust1_id)
        customer_serial = customer.serialize()

        self.assertEqual(customer_serial['id'], cust1_data['id'])
        self.assertEqual(customer_serial['name'], cust1_data['name'])
        self.assertEqual(customer_serial['phone'], cust1_data['phone'])
        self.assertEqual(customer_serial['address'], cust1_data['address'])

        self.assertIsInstance(customer_serial['notes'], list)
        self.assertEqual(customer_serial['notes']
                         [0]['note'], self.cust1_note_text)

    def test_has_note_from(self):
        # cust1 has a note, so the result should be true
        customer = Customer.query.get(cust1_id)
        self.assertTrue(customer.has_note_from(test_driver_id))

        # cust2 doesn't have a note, so the results should be false
        customer = customer.query.get(cust2_id)
        self.assertFalse(customer.has_note_from(test_driver_id))

    def test_make_id_from_phone(self):
        test_phone = '452-131-5131'
        id = Customer.make_id_from_phone(test_phone)

        self.assertEqual(id,
                         hashlib.md5(test_phone.encode()).hexdigest())

    def test_create_or_get_gets_a_customer(self):
        new_name = "New Name"
        test_customer = Customer.create_or_get(
            id=cust1_data['id'],
            name=new_name
        )
        self.assertEqual(test_customer.name, new_name)
        # just in case, we grab the customer from the db with the id,
        #   and sure enough, the name is updated
        cust1 = Customer.query.get(cust1_data['id'])
        self.assertEqual(cust1.name, new_name)

    def test_create_or_get_creates_a_customer(self):
        new_customer_data = {"id": '3',
                             "name": "testuser3",
                             "address": "Somewhere, anywhere",
                             "phone": "123-141-3132"}
        # to show the customer doesn't exist
        test_customer = Customer.query.get(new_customer_data['id'])
        self.assertIsNone(test_customer)

        customer = Customer.create_or_get(**new_customer_data)

        self.assertEqual(customer.id, new_customer_data['id'])
        # customer is now there
        test_customer = Customer.query.get(new_customer_data['id'])
        self.assertIsNotNone(test_customer)
