import datetime

DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"  # "Mon, 19 Apr 2021 00:00:00 GMT"


def get_date(date):
    return datetime.datetime.strptime(date, DATE_FORMAT).date()
