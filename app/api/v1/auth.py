import typing

from flask import g
from flask_httpauth import HTTPBasicAuth

from app.api.v1 import api_v1
from app.models import User
from .errors import unauthorized, UserValidateError, something_wrong

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
        user = User.verify_api_token(user_or_token)
        g.current_user = user
        g.is_api_token = True
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

@api_v1.errorhandler(UserValidateError)
def user_validate_error(e):
    return something_wrong(e.args[0])

@api_v1.after_request
def __after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,cache-control')
    response.headers.add('cache-control', 'no-cache')
    return response
