from flask import Blueprint, jsonify, session, g, request
from config import USER_SESSION_KEY, API_SESSION_KEY
from helpers.middleware import ensure_logged_in
from deliveries.models import Order
from users.models import User

order_api = Blueprint('order_api_routes', __name__)


# This is run before any route in this file
@order_api.before_request
def before_user_routes():
    #make sure if these functions return something, this whole function will return something
    logged_in = ensure_logged_in()
    if not logged_in:
        return jsonify(status=False, message="Not Logged In")
    

# @order_api.before_request
# def add_user_to_g_or_redirect():
#     """If we're logged in, add curr user to Flask global.
#     otherwise, redirect them to login"""
#     if USER_SESSION_KEY in session:
#         g.user = User.query.get(session[USER_SESSION_KEY])
#     else:
#         return jsonify(status=False, message="Not Logged In")


@order_api.route('/edit_tip', methods=["PATCH"])
def edit_order_tip():
    """edits a deliveries tip
    json input: id, tip """
    json = request.json
    if json:
        order_id = json.get('id')
        tip = json.get('tip')
        if order_id and tip:
            order = Order.query.get(order_id)
            if order:
                order.tip = tip
                order.update_db()
                return jsonify(status=True, order=order.serialize())
            else:
                return (jsonify(status=False, message=f"No order Found with id:{order_id} "), 404)
        else:
            return jsonify(status=False, message="missing id or tip from json PATCH")
    else:
        return jsonify(status=False, message="POST missing JSON")
