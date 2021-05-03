
def get_now_in(tz='US/Pacific'):
    pacific = pytz.timezone(tz)
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    return utc_now.astimezone(pacific)
