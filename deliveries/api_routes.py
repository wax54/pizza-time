from flask import Blueprint, jsonify
from deliveries.models import Note, Order

order_api = Blueprint('order_api_routes', __name__)


@order_api.route('/note/update', methods=["POST"])
def edit_order_note():
    """adds a note to the customer of a delivery
    json input: num, date, note """
    json = request.json
    order_num = json.get('num')
    order_date = json.get('date')
    new_note = json.get('note')
    # order_date = datetime.datetime.strptime(
    #     order_date, '%Y-%m-%dT%H:%M:%S.%fZ').date()
    if order_num and order_date and new_note:
        order = Order.get(num=order_num, date=order_date)
        if order:
            cust_id = order.cust_id
            driver_id = order.driver_id
            note = Note.create_or_update_note(
                cust_id=cust_id, driver_id=driver_id, new_note=new_note)
            if note:
                return jsonify(status=True, note=note.serialize())
            else:
                return (jsonify(status=False, message="There was an error with the DB"), 500)
        else:
            return (jsonify(status=False, message=f"No order Found with num:{order_num} and date:{order_date}"), 404)
    else:
        return jsonify(status=False, message="missing num or date or note from json POST")


@order_api.route('/note/delete', methods=["POST"])
def delete_order_note():
    """adds a note to the customer of a delivery
    json input: num, date, note """
    json = request.json
    order_num = json.get('num')
    order_date = json.get('date')
    # order_date = datetime.datetime.strptime(
    #     order_date, '%Y-%m-%dT%H:%M:%S.%fZ').date()
    if order_num and order_date:
        order = Order.get(num=order_num, date=order_date)
        if order:
            cust_id = order.cust_id
            driver_id = order.driver_id
            success = Note.delete(
                cust_id=cust_id, driver_id=driver_id)
            return jsonify(status=True)
        else:
            return (jsonify(status=False, message=f"No order Found with num:{order_num} and date:{order_date}"), 404)
    else:
        return jsonify(status=False, message="missing num or date or note from json POST")
