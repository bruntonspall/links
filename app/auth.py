from functools import wraps
from flask import redirect, request, g, request

USERS = ["michael@brunton-spall.co.uk", "test@example.com", "joel@slash32.co.uk", "michael@bruntonspall.com", "jonathan.lawrence@digital.justice.gov.uk"]

def check_user():
    user = users.get_current_user()
    g.user = user
    if user:
        if user.nickname() not in USERS:
            return "User {} is frobidden from accessing this page, <a href='{}'>logout</a>".format(user.nickname(), users.create_logout_url('/')), 403
        return None
    else:
        return "You need to <a href='{}'>login</a>".format(users.create_login_url(request.full_path))


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        ret = check_user()
        if not ret:
            return func(*args, **kwargs)
        else:
            return ret
    return decorated_view