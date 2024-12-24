from functools import wraps

from flask import abort, request
from flask_login import current_user

from app.models import Permission


def permission_required(perm):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.can(perm):
                abort(403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)


def header_required(head):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kw):
            if not request.headers.get(head):
                abort(403, {'message': '违规的访问'})
            return f(*args, **kw)

        return wrapper

    return decorator
