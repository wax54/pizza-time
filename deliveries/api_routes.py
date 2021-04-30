
@user_views.route('/edit_order_tip', methods=["PATCH"])
def edit_order_tip():
    """edits a deliveries tip
    json input: num, date, tip """
    json = request.json
    order_num = json.get('num')
    order_date = json.get('date')
    tip = json.get('tip')
    # order_date = datetime.datetime.strptime(
    #     order_date, '%Y-%m-%dT%H:%M:%S.%fZ').date()
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
