# -*- coding: utf-8 -*-
"""
    time_format.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

import time
import datetime


def time_to_utc_date(timestamp=None, formatter="%Y%m%d"):
    if not timestamp:
        timestamp = time.time()
    utc_date = datetime.datetime.utcfromtimestamp(timestamp).strftime(formatter)
    if utc_date.isdigit():
        return int(utc_date)
    else:
        return utc_date


def date_to_time(date, formatter="%Y%m%d"):
    utc = time.mktime(datetime.datetime.utcnow().timetuple())
    local = time.mktime(datetime.datetime.now().timetuple())
    diff = (local - utc) // 3600
    if not isinstance(date, str):
        date = str(int(date))
    timestamp = time.mktime(datetime.datetime.strptime(date, formatter).timetuple())
    timestamp += 3600 * diff
    return timestamp
