from flask import g
from users.models import WeekCode, Schedule
from api import PAG_KEY, DEMO_KEY


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
