import typing

from flask import g
from flask_httpauth import HTTPBasicAuth

from app.models import User
from .errors import unauthorized, UserValidateError

auth = HTTPBasicAuth()

if typing.TYPE_CHECKING:
    from flask import Response
    _response=Response

def validate_username_or_email(data):
    if data:
        if data.find('@') > -1:
            return {'email': data}
        else:
            return {'username': data}
    return False

@auth.verify_password
def verify_password(user_or_token, password):
    if user_or_token== '':
        return False
    if password == '':
        try:
            user = User.varify_api_token(user_or_token)
            g.current_user = user
            g.is_api_token = True
        except Exception:
            raise UserValidateError('验证码错误')
        return g.current_user is not None
    data = validate_username_or_email(user_or_token)
    if data:
        user = User.query.filter_by(**data).first()
        g.current_user = user
        g.is_api_token = False
        return user.validate_password(password)
    return False

@auth.error_handler
def auth_error():
    return unauthorized('用户登陆不成功')