from flask import Blueprint, redirect, jsonify, render_template, session, flash, g, request
from config import USER_SESSION_KEY, API_SESSION_KEY
from deliveries.models import Delivery, Order
from customers.models import Customer, Note
from users.models import User, Schedule, WeekCode
from users.utils import get_dollar_by_dow, get_dels_by_dow, get_total_hours, get_total_tips, get_hours_by_dow, update_schedule
from api import apis
from functools import reduce
import datetime
import urllib
import datetime
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
        if g.user:
            g.api = apis[g.user.api_id]
        else:
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
        orders_per_hour = total_dels/total_hours
    except ZeroDivisionError:
        orders_per_hour = 0

    try:
        tips_per_del = total_tips/total_dels
    except ZeroDivisionError:
        tips_per_del = 0
        
    try:
        tips_per_hour = total_tips/total_hours
    except ZeroDivisionError:
        tips_per_hour = 0
        

    dels_by_dow = reduce(get_dels_by_dow, orders, {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0
    })
    
    hours_by_dow = reduce(get_hours_by_dow, shifts, {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0
    })
    
    dollars_by_dow = reduce(get_dollar_by_dow, orders, {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0
    })
    dollars_per_hour_by_dow = {}
    dels_per_hour_by_dow = {}
    
    for (dow, hours) in hours_by_dow.items():
        try:
            dollars_per_hour = dollars_by_dow[dow]/hours
        except ZeroDivisionError:
            dollars_per_hour = 0
        dollars_per_hour_by_dow[dow] = round(dollars_per_hour, 2)
        
        try:
            dels_per_hour = dels_by_dow[dow]/hours
        except ZeroDivisionError:
            dels_per_hour = 0
        dels_per_hour_by_dow[dow] = round(dels_per_hour, 2)
    
    
    dollars_per_del_by_dow = {}
    for (dow, dollars) in dollars_by_dow.items():
        try:
            dollars_per_del = dollars/dels_by_dow[dow]
        except ZeroDivisionError:
            dollars_per_del = 0
        dollars_per_del_by_dow[dow] = round(dollars_per_del, 2)
    
    stats = [
    {
        "title": "TimeFrame",
        "result": STATS_TIMEFRAME
    }, {
        "title": "Deliveries Recorded",
        "result": total_dels
    }, {
        "title": "Tips",
        "result": f'${total_tips}'
    }, {
        "title": "Total hours Recorded",
        "result": f'{total_hours}Hrs'
    }, 
        {
        "title": "Orders/Hour",
        "desc": "Avg amount of dollars made per hour worked (according to your schedule)",
        "result": f'{round(orders_per_hour, 2)}'
    }, {
        "title": "Dollars/Hour",
        "desc": "Avg amount of dollars made per hour worked (according to your schedule)",
        "result": f'${round(tips_per_hour, 2)}'
    },  {
        "title": "Dollars/Delivery",
        "desc": "Avg amount of tips made per delivery",
        "result": f'${round(tips_per_del, 2)}'
    }
    ]
    
    dow_avgs = [{"title": "Hours Worked", "data": hours_by_dow},
                {"title":"Deliveries", "data":dels_by_dow},
                {"title":"Dollars", "data": dollars_by_dow},
                {"title": "Average $/Hr", "data": dollars_per_hour_by_dow},
                {"title": "Average Orders/Hr", "data": dels_per_hour_by_dow},
                {"title": "Average $/Order", "data": dollars_per_del_by_dow}
                ]
    return render_template('stats_page.html', stats=stats, dow_stats=dow_avgs)


@user_views.route('/show_schedule')
def show_schedule():
    # update_schedule.
    update_schedule(g.user)
    # show all schedules in DB
    shifts = Schedule.get_future_shifts(g.user.id)
    return render_template('schedule_page.html', shifts=shifts, datetime=datetime)
