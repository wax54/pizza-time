# Code Copied From
# https://www.peterbe.com/plog/best-practice-with-retries-with-requests

import datetime
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def request_with_retry(
    retries=3,
    backoff_factor=0.8,
    status_forcelist=(404, 500),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=False
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"  # "Mon, 19 Apr 2021 00:00:00 GMT"


def get_date(date):
    return datetime.datetime.strptime(date, DATE_FORMAT).date()
