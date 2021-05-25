from flask import g
from users.models import WeekCode, Schedule
from api import PAG_KEY, DEMO_KEY
import tz_utils
import datetime

def make_date_time_from_now(days=0, hours=0):
    """a function that returns a string 
    representing a time that is 'days' days 
    and 'hours' hours away from now"""
    now = tz_utils.get_now_in(tz='UTC')
    date_time = now + datetime.timedelta(days=days, hours=hours)
    return date_time

def get_dollar_by_dow(dow_counter, order):
    dow = order.date.weekday()
    dow_counter[dow] = get_total_tips(dow_counter[dow], order)
    return dow_counter

def get_dels_by_dow(dow_counter, order):
    dow = order.date.weekday()
    dow_counter[dow] += 1
    return dow_counter


def get_hours_by_dow(dow_counter, shift):
    hours = shift.get_shift_hours()
    dow = shift.start.weekday()
    dow_counter[dow] += hours
    return dow_counter



def get_total_tips(total, order):
    return total + order.tip


def get_total_hours(total_hours, shift_to_add):
    hours = shift_to_add.get_shift_hours()
    return total_hours + hours


def update_schedule(user):
    # check for old schedule codes
    codes = WeekCode.get_codes_for_user(user.id)

    # send old schedule codes with the request
    schedules = g.api.get_schedules(
        email=user.email, token=user.token, ignore=codes)
    # if a new schedule pops up,
    if schedules:
        if user.api_id == PAG_KEY:
            Schedule.add_from_pag(schedules=schedules, user_id=user.id)
        if user.api_id == DEMO_KEY:
            Schedule.add_from_demo(schedules=schedules, user_id=user.id)
