from flask import Blueprint, redirect, jsonify, session, g, request
from helpers.middleware import ensure_logged_in
from config import USER_SESSION_KEY, API_SESSION_KEY
from customers.models import Customer, Note
from users.models import User

customer_api = Blueprint('customer_api_routes', __name__)

# This is run before any route in this file
@customer_api.before_request
def before_user_routes():
    #make sure if these functions return something, this whole function will return something
    logged_in = ensure_logged_in()
    if not logged_in:
        return jsonify(status=False, message="Not Logged In")



# @customer_api.before_request
# def add_user_to_g_or_redirect():
#     """If we're logged in, add curr user to Flask global.
#     otherwise, redirect them to login"""
#     if USER_SESSION_KEY in session:
#         g.user = User.query.get(session[USER_SESSION_KEY])
#     else:
#         g.user = None


@customer_api.route('/note/update', methods=["POST"])
def edit_order_note():
    """adds a note to a customer as yourself
    json input: customer_id, note """
    driver = g.get('user')
    if driver:
        json = request.json
        if json:
            driver_id = driver.id
            cust_id = json.get('customer_id')
            new_note = json.get('note')

            if cust_id and new_note:
                note = Note.create_or_update_note(
                    cust_id=cust_id, driver_id=driver_id, new_note=new_note)
                if note:
                    return jsonify(status=True, note=note.serialize())
                else:
                    return (jsonify(status=False, message="There was an error entering your data, please check it and try again."), 500)
            else:
                return jsonify(status=False, message="missing customer_id or new_note from json POST")
        else:
            return jsonify(status=False, message="POST missing JSON")
    else:
        return jsonify(status=False, message="Not Logged In")


@customer_api.route('/note/delete', methods=["POST"])
def delete_order_note():
    """adds a note to the customer of a delivery
    json input: customer_id """
    driver = g.get('user')
    if driver:
        json = request.json
        if json:
            driver_id = driver.id
            cust_id = json.get('customer_id')
            if cust_id:
                success = Note.delete(
                    cust_id=cust_id, driver_id=driver_id)
                if success:
                    return jsonify(status=True)
                else:
                    return jsonify(status=False, message="Error finding specified note...")
            else:
                return jsonify(status=False, message="Missing customer_id from json POST")
        else:
            return jsonify(status=False, message="POST missing JSON")
    else:
        return jsonify(status=False, message="Not Logged In")
