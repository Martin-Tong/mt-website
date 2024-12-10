from flask import g, request

from app.api.v1 import api_v1
from app.api.v1.auth import auth
from app.models import User, Post
from .errors import forbidden, something_wrong, UserValidateError


@api_v1.before_request
@auth.login_required
def before_request():
    pass

@api_v1.errorhandler(UserValidateError)
def user_validate_error(e):
    return something_wrong(e.args[0])

@api_v1.after_request
def __after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,cache-control')
    response.headers.add('cache-control', 'no-cache')
    return response

@api_v1.route('/get-token', methods=['GET'])
def get_token():
    if g.current_user and g.current_user.can(63):
        return {'status':'success','token': g.current_user.generate_api_token()}
    return forbidden('没有权限')

@api_v1.route('/get-user')
def get_user():
    name = request.args.get('name')
    if name:
        user = User.query.filter_by(username = name).first()
        if user:
            return {'users': [user.to_json()]}
        else:
            return something_wrong('查询的用户不存在')
    else:
        user = User.query.filter(User.id != g.current_user.id).all()
    return {'current_user': g.current_user.to_json(), 'users': [i.to_json() for i in list(user)]}

@api_v1.route('/get-post')
def get_post():
    _id = request.args.get('id')
    if _id:
        posts = Post.query.get(_id)
        if not posts:
            return something_wrong('查询的文章不存在')
        return {'posts': [post.to_json() for post in [posts]]}
    else:
        posts = Post.query.all()
    return {'posts': [post.to_json() for post in list(posts) ]}