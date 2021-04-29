from flask import Blueprint, redirect, jsonify, render_template, session, flash, g, request
from config import USER_SESSION_KEY, API_SESSION_KEY
from deliveries.models import Delivery, Order
from customers.models import Customer, Note
from users.models import User, Schedule, WeekCode
from api import apis
from functools import reduce
import datetime
import urllib
user_views = Blueprint('user_routes', __name__)


def urlencode(string):
    return urllib.parse.quote_plus(string)

# This is run before any route in this file


@user_views.before_request
def add_user_to_g_or_redirect():
    """If we're logged in, add curr user to Flask global.
    otherwise, redirect them to login"""
    if USER_SESSION_KEY in session:
        g.user = User.query.get(session[USER_SESSION_KEY])
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
        flash("Error validating against API, Please try logging in, again. Thanks!")
        return redirect('/login')
    if delivery['orders'] == []:
        # no delivery found
        flash("No Delivery Found!", "info")
    if delivery['orders']:
        # successful credentials and delivery found
        d = Delivery.save_delivery(delivery=delivery, driver_id=g.user.id)

        # So now we have the variable delivery,
        #       A plain object the API gave us
        #       with a date key and an orders key containing and array of orders
        # and we have the variable d,
        #       Which is the concept of the Database delivery we found or made.
        #       If we found any orders in the DB, they may have tip info that we want to retain
        # We want to use the API delivery object because it has the address and the phone.
        #       But, we want to get the tip from the db object and add
        #       it to the API Object(which currently has no Tip Attr)

        # this is real rough, should clean this up....
        for curr_order in delivery['orders']:
            # find the order in the db orders
            # it feels like there is a better way to do this
            # but its only every like 2 or three orders at a time
            for order in d.orders:
                if order.num == curr_order['num']:
                    db_order = order
                    curr_order['tip'] = db_order.tip
                    curr_order['date'] = db_order.date
                    curr_order['customer'] = db_order.customer
                    
    return render_template('deliveries/current_delivery.html', delivery=delivery, name=g.user.name)


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


@user_views.route('/edit_deliveries')
def edit_delvieries():
    orders = Order.get_orders_for(g.user.id)
    return render_template("deliveries/list_all_orders.html", all_orders=orders)

# TODO
# right a view function that just displays the deliveries for a certain date range, or a certain day
# @user_views.route('/edit_deliveries')
# def edit_delvieries():
#     orders = Order.get_orders_for(g.user.id)
#     return render_template("deliveries/list_all_orders.html", all_orders=orders)


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

