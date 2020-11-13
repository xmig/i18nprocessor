"""
Set of utils for time manipulation
"""

from datetime import datetime, timezone, timedelta
import time

from dateutil import parser


_default_format_datetime = '%Y-%m-%d %H:%M:%S'


def time_as_string(time_val=None, time_fmt=None):
    """ Returns time in form 'YYYY-MM-DD hh:mm:ss'
    :param timeval:  datetime
    :param time_fmt: str @example '%Y-%m-%d %H:%M:%S'
    """

    time_val = time_val or datetime.now()
    time_fmt = time_fmt or _default_format_datetime

    assert(issubclass(type(time_val), datetime))

    return time_val.strftime(time_fmt)


def timestamp(future_seconds=0):
    return time.time() + int(future_seconds)


def hour_subtract(same_date, hours):
    return same_date - timedelta(hours=hours)


def sting_to_date(date_str):
    return parser.parse(date_str)


def date_time_now():
    local_timezone = datetime.now(timezone.utc).astimezone(timezone.utc).tzinfo
    date_time_now = datetime.now(local_timezone.utc)
    return date_time_now
