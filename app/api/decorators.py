import functools

from flask import g

from app.api.v1.errors import forbidden


def permission_required(perm):
    def decorator(f):
        @functools.wraps(f)
        def wraps(*args, **kw):
            if not g.current_user.can(perm):
                return forbidden('没有权限')
            return f(*args, **kw)
        return wraps
    return decorator
