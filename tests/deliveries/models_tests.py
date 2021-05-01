from unittest import TestCase
from app import app
from db_setup import db

from users.models import User
from customers.models import Customer
from deliveries.models import *

import datetime

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///pizza_time_test'
app.config['SQLALCHEMY_ECHO'] = False


def seed_db():
    db.session.rollback()
    global test_driver_id
    global test_cust_id
    global test_delivery_id
    global test_order_id
    global order_data

    db.drop_all()
    db.create_all()

    user_data = {"email": "test@email.com", "token": "testToken"}

    cust_data = {"id": '1',
                 "name": "testuser1",
                 "address": "Some Address",
                 "phone": "203-881-7843"}

    test_driver = User(**user_data)
    test_cust = Customer(**cust_data)

    db.session.add(test_cust)
    db.session.add(test_driver)

    db.session.commit()

    delivery_data = {"driver_id": test_driver.id}

    test_delivery = Delivery(**delivery_data)

    db.session.add(test_delivery)

    db.session.commit()
    order_data = {"num": 112,
                  "cust_id": test_cust.id,
                  "del_id": test_delivery.id,
                  "driver_id": test_driver.id,
                  "date": datetime.date(2021, 4, 19)}

    test_order = Order(**order_data)

    db.session.add(test_order)
    db.session.commit()

    test_driver_id = test_driver.id
    test_cust_id = test_cust.id
    test_delivery_id = test_delivery.id
    test_order_id = (test_order.num, test_order.date)


class DeliveryTests(TestCase):
    def setUp(self):
        seed_db()

    def test_delivery_has_expected_params(self):
        delivery = Delivery.query.get(test_delivery_id)

        self.assertEqual(delivery.driver_id, test_driver_id)

        self.assertIsInstance(delivery.orders, list)
        order = delivery.orders[0]
        self.assertEqual((order.num, order.date), test_order_id)

        self.assertEqual(delivery.driver.id, test_driver_id)

    def test_save_delivery(self):
        TEST_DELIVERY_DATA = {"orders": [{"num": 115,
                                          "name": "Kassandra Meyers",
                                          "address": "12525 NE 32nd St Bellevue, WA. 98005",
                                          "phone": "425-155-1443"},
                                         {"num": 117,
                                          "name": "Bernadett Winthrop",
                                          "address": "3050 125th Ave NE Bellevue, WA. 98005",
                                          "phone": "425-555-8972"}],
                              "date": datetime.date(2020, 4, 17)}

        delivery = Delivery.save_delivery(
            TEST_DELIVERY_DATA,
            test_driver_id
        )

        self.assertEqual(delivery.driver_id, test_driver_id)

        self.assertIsInstance(delivery.orders, list)
        self.assertEqual(len(delivery.orders), 2)


class OrderTests(TestCase):
    def setUp(self):
        seed_db()

    def test_order_has_expected_params(self):
        order = Order.query.get(test_order_id)

        self.assertEqual(order.num, order_data['num'])
        self.assertEqual(order.date, order_data['date'])
        self.assertEqual(order.tip, 0)
        self.assertEqual(order.del_id, order_data['del_id'])
        self.assertEqual(order.cust_id, order_data['cust_id'])
        self.assertEqual(order.driver_id, order_data['driver_id'])

        self.assertEqual(order.driver.id, test_delivery_id)
        self.assertEqual(order.customer.id, test_cust_id)

#     def test_serialize_has_expected_params(self):
#         customer = Customer.query.get(cust1_id)
#         customer_serial = customer.serialize()

#         self.assertEqual(customer_serial['id'], cust1_data['id'])
#         self.assertEqual(customer_serial['name'], cust1_data['name'])
#         self.assertEqual(customer_serial['phone'], cust1_data['phone'])
#         self.assertEqual(customer_serial['address'], cust1_data['address'])

#         self.assertIsInstance(customer_serial['notes'], list)
#         self.assertEqual(customer_serial['notes']
#                          [0]['note'], self.cust1_note_text)

    def test_save_delivery(self):
        TEST_DELIVERY_DATA = {"orders": [{"num": 115,
                                          "name": "Kassandra Meyers",
                                          "address": "12525 NE 32nd St Bellevue, WA. 98005",
                                          "phone": "425-155-1443"},
                                         {"num": 117,
                                          "name": "Bernadett Winthrop",
                                          "address": "3050 125th Ave NE Bellevue, WA. 98005",
                                          "phone": "425-555-8972"}],
                              "date": datetime.date(2020, 4, 17)}

        delivery = Delivery.save_delivery(
            TEST_DELIVERY_DATA,
            test_driver_id
        )

        self.assertEqual(delivery.driver_id, test_driver_id)

        self.assertIsInstance(delivery.orders, list)
        self.assertEqual(len(delivery.orders), 2)


# class CustomerTests(TestCase):

#     def setUp(self):
#         seed_db()
#         self.cust1_note_text = "TEST_NOTE_TEXT"

#         Note.query.delete()

#         note = Note(driver_id=test_driver_id,
#                     cust_id=cust1_id,
#                     note=self.cust1_note_text)
#         db.session.add(note)
#         db.session.commit()

#     def test_customer_has_expected_params(self):
#         customer = Customer.query.get(cust1_id)

#         self.assertEqual(customer.id, cust1_data['id'])
#         self.assertEqual(customer.name, cust1_data['name'])
#         self.assertEqual(customer.phone, cust1_data['phone'])
#         self.assertEqual(customer.address, cust1_data['address'])

#         self.assertIsInstance(customer.notes, list)
#         self.assertEqual(customer.notes[0].note, self.cust1_note_text)

#         self.assertIsInstance(customer.orders, list)

#     def test_serialize_has_expected_params(self):
#         customer = Customer.query.get(cust1_id)
#         customer_serial = customer.serialize()

#         self.assertEqual(customer_serial['id'], cust1_data['id'])
#         self.assertEqual(customer_serial['name'], cust1_data['name'])
#         self.assertEqual(customer_serial['phone'], cust1_data['phone'])
#         self.assertEqual(customer_serial['address'], cust1_data['address'])

#         self.assertIsInstance(customer_serial['notes'], list)
#         self.assertEqual(customer_serial['notes']
#                          [0]['note'], self.cust1_note_text)

#     def test_has_note_from(self):
#         # cust1 has a note, so the result should be true
#         customer = Customer.query.get(cust1_id)
#         self.assertTrue(customer.has_note_from(test_driver_id))

#         # cust2 doesn't have a note, so the results should be false
#         customer = customer.query.get(cust2_id)
#         self.assertFalse(customer.has_note_from(test_driver_id))

#     def test_make_id_from_phone(self):
#         test_phone = '452-131-5131'
#         id = Customer.make_id_from_phone(test_phone)

#         self.assertEqual(id,
#                          hashlib.md5(test_phone.encode()).hexdigest())

#     def test_create_or_get_gets_a_customer(self):
#         new_name = "New Name"
#         test_customer = Customer.create_or_get(
#             id=cust1_data['id'],
#             name=new_name
#         )
#         self.assertEqual(test_customer.name, new_name)
#         # just in case, we grab the customer from the db with the id,
#         #   and sure enough, the name is updated
#         cust1 = Customer.query.get(cust1_data['id'])
#         self.assertEqual(cust1.name, new_name)

#     def test_create_or_get_creates_a_customer(self):
#         new_customer_data = {"id": '3',
#                              "name": "testuser3",
#                              "address": "Somewhere, anywhere",
#                              "phone": "123-141-3132"}
#         # to show the customer doesn't exist
#         test_customer = Customer.query.get(new_customer_data['id'])
#         self.assertIsNone(test_customer)

#         customer = Customer.create_or_get(**new_customer_data)

#         self.assertEqual(customer.id, new_customer_data['id'])
#         # customer is now there
#         test_customer = Customer.query.get(new_customer_data['id'])
#         self.assertIsNotNone(test_customer)
