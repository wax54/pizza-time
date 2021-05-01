from flask import Blueprint, jsonify, session, g, request
from config import USER_SESSION_KEY, API_SESSION_KEY
from customers.models import Customer, Note
from users.models import User

order_api = Blueprint('order_api_routes', __name__)


@order_api.before_request
def add_user_to_g_or_redirect():
    """If we're logged in, add curr user to Flask global.
    otherwise, redirect them to login"""
    if USER_SESSION_KEY in session:
        g.user = User.query.get(session[USER_SESSION_KEY])
    else:
        return jsonify(status=False, message="Not Logged In")


@user_views.route('/edit_tip', methods=["PATCH"])
def edit_order_tip():
    """edits a deliveries tip
    json input: num, date, tip """
    json = request.json
    if json:
        order_num = json.get('num')
        order_date = json.get('date')
        tip = json.get('tip')
        if order_num and order_date and tip:
            order = Order.get(num=order_num, date=order_date)
            if order:
                order.tip = tip
                order.update_db()
                return jsonify(status=True, order=order.serialize())
            else:
                return (jsonify(status=False, message=f"No order Found with num:{order_num} and date:{order_date}"), 404)
        else:
            return jsonify(status=False, message="missing num or date or tip from json PATCH")
    else:
        return jsonify(status=False, message="POST missing JSON")
