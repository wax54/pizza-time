from flask import Blueprint, redirect, jsonify, render_template, session, flash, g, request
from config import USER_KEY, API_SESSION_KEY
from deliveries.models import Delivery
from users.models import User, Schedule, WeekCode
from api import pag_api, demo_api
from functools import reduce
import datetime


apis = {
    "pag": pag_api,
    "demo": demo_api
}

user_views = Blueprint('user_routes', __name__)


# This is run before anything in this file
@user_views.before_request
def add_user_to_g_or_redirect():
    """If we're logged in, add curr user to Flask global.
    otherwise, redirect them to login"""

    if USER_KEY in session:
        g.user = User.query.get(session[USER_KEY])
        g.api = apis[session[API_SESSION_KEY]]
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
    delivery = g.api.get_delivery(email=email, token=token)
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
    STATS_TIMEFRAME = datetime.timedelta(days=7)

    def within_stat_timeframe(date):
        today = datetime.date.today()
        return date <= today and date >= today - STATS_TIMEFRAME
    u_id = g.user.id
    # figures
    all_orders = g.user.orders

    # STATS TIMEFRAME STUFF!
    shifts = Schedule.get_last(user_id=u_id, delta=STATS_TIMEFRAME)
    orders = [o for o in all_orders if within_stat_timeframe(o.date)]

    total_dels = len(orders)
    total_tips = reduce(get_total_tips, orders, 0)
    total_hours = reduce(get_total_hours, shifts, 0)
    try:
        tips_per_del = total_tips/total_dels
        tips_per_hour = total_tips/total_hours
    except ZeroDivisionError:
        tips_per_del = 0
        tips_per_hour = 0
    dels_per_day_of_week = reduce(get_dels_as_dow, orders, {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0
    })

    stats = [{
        "title": "Total Orders",
        "result": total_dels
    }, {
        "title": "Total Tips Earned",
        "result": f'${total_tips}'
    }, {
        "title": "Total hours Recorded",
        "result": f'{total_hours}'
    }, {
        "title": "Dollars/Hour",
        "desc": "Avg amount of dollars made hour worked (according to your schedule)",
        "result": f'${round(tips_per_hour, 2)}'
    },  {
        "title": "tips/Delivery",
        "desc": "Avg amount of tips made per delivery",
        "result": f'${round(tips_per_del, 2)}'
    }, {
        "title": "Orders per Day of Week",
        "desc": "Number of orders taken per day of week in last STAT_TIMEFRAME",
        "result": dels_per_day_of_week
    }
    ]
    return render_template('stats_page.html', stats=stats)


def get_dels_as_dow(dow_counter, order):
    dow = order.date.weekday()
    dow_counter[dow] += 1
    return dow_counter


def get_total_tips(total, order):
    return total + order.tip


def get_total_hours(total_hours, shift_to_add):
    delta = shift_to_add.get_shift_length()
    # 60 seconds in a min, 60 mins in a hour
    hours = delta.total_seconds() / 60 / 60
    return total_hours + hours


@user_views.route('/show_schedule')
def show_schedule():
    # update_schedule.
    update_schedule(g.user)
    # show all schedules in DB
    shifts = Schedule.get_future_shifts(g.user.id)
    return render_template('schedule_page.html', shifts=shifts)


def update_schedule(user):
    # check for old schedule codes
    codes = WeekCode.get_codes_for_user(user.id)

    # send old schedule codes with the request
    schedules = g.api.get_schedules(
        email=user.email, token=user.token, ignore=codes)
    # if a new schedule pops up,

    if schedules:
        if session[API_SESSION_KEY] == "pag":
            Schedule.add_from_pag(schedules=schedules, user_id=user.id)
        if session[API_SESSION_KEY] == "demo":
            Schedule.add_from_demo(schedules=schedules, user_id=user.id)
