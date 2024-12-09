from flask import g, request

from app.api.v1 import api_v1
from app.api.v1.auth import auth
from .errors import forbidden

from app.models import User


@api_v1.before_request
@auth.login_required
def before_request():
    pass

@api_v1.route('/get-token', methods=['GET'])
def get_token():
    print(g.__dict__)
    if g.current_user and g.current_user.can(63):
        return {'status':'success','token': g.current_user.generate_api_token()}
    return forbidden('没有权限')

@api_v1.route('/get-user')
def get_user():
    name = request.args.get('name')
    if name:
        print(name)
        user = [User.query.filter_by(username = name).first()]
        return {'users': user[0].to_json()}
    else:
        user = User.query.filter(User.id != g.current_user.id).all()
    return {'current_user': g.current_user.to_json(), 'users': [i.to_json() for i in user]}

