from flask import session
from functools import wraps


def check_logged_in(func):
    @wraps(func)
    def wrapper(*args, **kwagrs):
        if 'logging_in' in session:
            return func(*args, **kwagrs)
        return 'You are not logged in!'
    return wrapper