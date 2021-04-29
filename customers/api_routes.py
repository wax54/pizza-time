from flask import Blueprint, redirect, jsonify, session, g, request
from config import USER_SESSION_KEY, API_SESSION_KEY
from customers.models import Customer, Note
from users.models import User

customer_api = Blueprint('customer_api_routes', __name__)


@customer_api.before_request
def add_user_to_g_or_redirect():
    """If we're logged in, add curr user to Flask global.
    otherwise, redirect them to login"""
    if USER_SESSION_KEY in session:
        g.user = User.query.get(session[USER_SESSION_KEY])
    else:
        g.user = None


@customer_api.route('/note/update', methods=["POST"])
def edit_order_note():
    """adds a note to a customer as yourself
    json input: customer_id, note """
    json = request.json
    cust_id = json.get('customer_id')
    driver_id = g.get('user').id
    new_note = json.get('note')
    if driver_id:
        if cust_id and new_note:
            note = Note.create_or_update_note(
                cust_id=cust_id, driver_id=driver_id, new_note=new_note)
            if note:
                return jsonify(status=True, note=note.serialize())
            else:
                return (jsonify(status=False, message="There was an error with the DB"), 500)
        else:
            return jsonify(status=False, message="missing customer_id or new_note from json POST")
    else:
        return jsonify(status=False, message="Not Logged In")


@customer_api.route('/note/delete', methods=["POST"])
def delete_order_note():
    """adds a note to the customer of a delivery
    json input: num, date, note """
    json = request.json
    cust_id = json.get('customer_id')
    driver_id = g.get('user').id
    if driver_id:
        if cust_id:
            success = Note.delete(
                cust_id=cust_id, driver_id=driver_id)
            return jsonify(status=True)
        else:
            return jsonify(status=False, message="missing cust_id from json POST")
    else:
        return jsonify(status=False, message="Not Logged In")
