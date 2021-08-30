from flask import Blueprint, redirect, jsonify, render_template, session, flash, g, request
from config import RENEWAL_TIMEFRAME, USER_SESSION_KEY, API_SESSION_KEY, ACCESSOR_SESSION_KEY, JWT_AUTH_KEY, SECRET_KEY
from deliveries.models import Delivery, Order
from customers.models import Customer, Note
from users.models import User, Schedule, WeekCode
from users.utils import get_dollar_by_dow, get_dels_by_dow, get_total_hours, get_total_tips, get_hours_by_dow, update_schedule
from helpers.middleware import ensure_logged_in, keep_user_accessor_up_to_date ,keep_api_token_up_to_date
from api import apis
from functools import reduce
import datetime
import urllib
import datetime
import tz_utils
import pytz
import jwt

user_views = Blueprint('user_routes', __name__)
#used for tokens and accessors - anything with less than 3 days of life left gets renewed
RENEWAL_TIMEFRAME = datetime.timedelta(days=3)



def update_token():
    token = g.user.token
    email = g.user.email

    print("Updating token for user ", g.user.id)
    #token is expired, do something!
    new_token_glob = g.api.re_auth(email=email, token=token)
    if(new_token_glob):
        new_token = new_token_glob['token']
        expiration = new_token_glob['expiration']
        g.user.update_token(token=new_token,
                            token_expiration=expiration)
        print("Token updated for user ", g.user.id)

    else:
        print(f'Failed fetching token for user {g.user.id}')

def keep_api_token_up_to_date():
    token_expiration = g.user.token_expiration
    #if there is no expiration, update the token
    if not token_expiration:
        return update_token()
    
    #assumed token expiration is in UTC
    token_expiration = tz_utils.get_time_as_utc(token_expiration, 'UTC')

    if (token_expiration - tz_utils.get_now_in(tz='UTC')) < RENEWAL_TIMEFRAME:
        return update_token()


def keep_user_accessor_up_to_date(response):
    if g.user:
        curr_expiration = g.user.accessor_expiration
        curr_expiration = pytz.utc.localize(curr_expiration)
        # seeing if the accessor has less than RENEWAL_TIMEFRAME TTL
        if (curr_expiration - tz_utils.get_now_in(tz='UTC')) < RENEWAL_TIMEFRAME:
            #accessor is expired!
            g.user.update_accessor()
            user_jwt = g.user.make_jwt()
            # put the auth in the cookies
            response.set_cookie(JWT_AUTH_KEY, user_jwt,
                            expires=g.user.accessor_expiration)
    return response
    

def ensure_logged_in():
    """If we're logged in, add curr user to Flask global.
    otherwise, redirect them to login"""
    # if USER_SESSION_KEY in session:
    if g.user:
        return True
    else:
        return False

# This is run before any route in this file
@user_views.before_request
def before_user_routes():
    #make sure if these functions return something, this whole function will return something
    logged_in = ensure_logged_in()
    if logged_in:
        #adds the current API to G
        g.api = apis[g.user.api_id]
    else:
        flash("Please Log In!")
        return redirect("/login")
    keep_api_token_up_to_date()



@user_views.after_request
def after_user_routes(resp): 
    resp = keep_user_accessor_up_to_date(resp)
    return resp



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
        d = Delivery.save_delivery(delivery=delivery, driver_id=g.user.id, api_id = g.user.api_id)

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
                    curr_order['id'] = db_order.id
                    curr_order['tip'] = db_order.tip
                    curr_order['customer'] = db_order.customer
    print(delivery)
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
    update_schedule(g.user)
    
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
        dollars_per_hour_by_dow[dow] = f'${round(dollars_per_hour, 2)}'
        
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
        dollars_per_del_by_dow[dow] = f'${round(dollars_per_del, 2)}'
    
    stats = [
    {
        "title": "Time Frame",
        "result": f'Last {STATS_TIMEFRAME.days} Days'
    }, {
        "title": "Deliveries Recorded",
        "result": total_dels
    }, {
        "title": "Tips",
        "result": f'${round(total_tips, 2)}'
    }, {
        "title": "Total hours Recorded",
        "result": f'{total_hours}Hrs'
    }, 
        {
        "title": "Orders/Hour",
        "desc": "Avg amount of orders delivered per hour worked (according to your schedule)",
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
    # show all shifts from today or later
    shifts = Schedule.get_future_shifts(g.user.id)
    now = tz_utils.get_now_in('US/Pacific')
    return render_template('schedule_page.html', shifts=shifts, today=now)

