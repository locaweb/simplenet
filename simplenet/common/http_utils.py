from functools import wraps
from bottle import response

try:
    from simplejson import dumps
except ImportError:
    from json import dumps


def reply_json(f):
    @wraps(f)
    def json_dumps(*args, **kwargs):
        r = f(*args, **kwargs)
        response.content_type = "application/json; charset=UTF-8"
        if r and type(r) in (dict, list, tuple):
            return dumps(r)
        if r and type(r) is str:
            return r
    return json_dumps
