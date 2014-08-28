import os
from functools import wraps
from flask import request, Response


def check_auth(username, password):
    return username == 'basic' and password == os.environ['API_KEY']

def forbidden():
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return forbidden()
        return f(*args, **kwargs)
    return decorated
