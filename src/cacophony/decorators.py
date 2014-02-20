from flask import abort, request


def remote_user_required(f):
    """
    Ensures a user has authenticated with the proxy.
    """
    def decorator(*args, **kwargs):
        if not request.remote_user:
            abort(401)
        return f(*args, **kwargs)
    return decorator
