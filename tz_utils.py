import pytz
import datetime

def get_now_in(tz='US/Pacific'):
    output_tz = pytz.timezone(tz)
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    return utc_now.astimezone(output_tz)


def get_time_as_utc(time, input_tz='US/Pacific'):
    from_tz = pytz.timezone(input_tz)
    local_dt = from_tz.localize(time)
    return local_dt.astimezone(pytz.utc)
