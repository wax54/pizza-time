from flask import Blueprint, redirect, jsonify, render_template, session, flash, g, request
from config import USER_KEY
from deliveries.models import Delivery
from users.models import User, Schedule, PagCode
import api.pag_api as api
import datetime
user_views = Blueprint('user_routes', __name__)


# This is run before anything in this file
@user_views.before_request
def add_user_to_g_or_redirect():
    """If we're logged in, add curr user to Flask global.
    otherwise, redirect them to login"""

    if USER_KEY in session:
        g.user = User.query.get(session[USER_KEY])
        if not g.user:
            flash("Please Log In!")
            return redirect('/login')
    else:
        flash("Please Log In!")
        return redirect('/login')


@user_views.route('/current_delivery')
def show_current_delviery():
    token = g.user.token
    email = g.user.email
    delivery = api.get_delivery(email=email, token=token)
    if delivery == False:
        # validation error
        return redirect('/login')
    if delivery['orders'] == []:
        # no delivery found
        flash("No Delivery Found!", "info")
    if delivery['orders']:
        # successful credentials and delivery found
        d = Delivery.save_delivery(delivery=delivery, driver_id=g.user.id)
        # this is real rough, should clean this up....
        for i in range(len(d.orders)):
            delivery['orders'][i]['tip'] = d.orders[i].tip

    return render_template('deliveries/current_delivery.html', delivery=delivery, name=g.user.name)


@user_views.route('/edit_order_tip', methods=["PATCH"])
def edit_order_tip():
    """edits a deliveries tip
    json input: id, tip """
    json = request.json()
    order_id = json('id')
    tip = json.get('tip')
    if order_id and tip:
        order = Order.query.get(order_id)
        if order:
            order.tip = tip
            return jsonify(status=True, order=order.serialize())
        else:
            return jsonify(status=False, message=f"No order Found with id:{order_id}")
    else:
        return jsonify(status=False, message="missing id or tip from json PATCH")


@user_views.route('/edit_deliveries')
def edit_delvieries():
    orders = g.user.orders
    return render_template("deliveries/list_orders.html", orders=orders)


@user_views.route('/dashboard')
def show_stats():
    #figures
    orders = g.user.orders
    shifts = g.user.shifts

    total_dels = len(orders)
    total_tips = get_total_tips(orders)

    #shift_hours =
    print("##############################")
    print(shifts[0].get_shift_length())

    dol_per_del = total_tips/total_dels
    stats = [{
        "title": "Total Orders",
        "result": total_dels
    }, {
        "title": "Total Tips Earned",
        "result": f'${total_tips}'
    }, {
        "title": "Dollars/Delivery",
        "desc": "Avg amount of dollars made per delivery",
        "result": f'${dol_per_del}'
    }
    ]
    return render_template('stats_page.html', stats=stats)


def get_total_tips(orders):
    total = 0
    for order in orders:
        total += order.tip
    return total


@user_views.route('/show_schedule')
def show_schedule():
    # update_schedule.
    update_schedule(g.user)
    # show all schedules in DB
    shifts = Schedule.get_future_shifts(g.user.id)
    return render_template('schedule_page.html', shifts=shifts)


def update_schedule(user):
    # TODO
    # check for old schedule codes
    codes = PagCode.get_codes_for_user(user.id)

    # send old schedule codes with the request
    schedules = api.get_schedules(
        email=user.email, token=user.token, ignore=codes)
    # if a new schedule pops up,
    if schedules:
        Schedule.update_from_pag(schedules=schedules, user_id=user.id)
