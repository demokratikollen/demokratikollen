from flask.ext.cache import Cache
import os
# Setup the Cache
cache = Cache(config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': str(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) + '/cache'})


#make a http last modified wrapper
from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime,timedelta

def httpdate(dt):
    """Return a string representation of a date according to RFC 1123
    (HTTP/1.1).

    The supplied date must be in UTC.

    """
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
             "Oct", "Nov", "Dec"][dt.month - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
        dt.year, dt.hour, dt.minute, dt.second)

def http_expires(seconds):
    def decorator(view):
        @wraps(view)
        def http_caching_wrapper(*args, **kwargs):
            response = make_response(view(*args, **kwargs))
            response.headers['Expires'] = httpdate(datetime.now() + timedelta(seconds=seconds))
            return response 
        return update_wrapper(http_caching_wrapper, view)

    return decorator