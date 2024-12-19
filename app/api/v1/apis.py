from flask import g, request, jsonify

from app import db
from app.api.v1 import api_v1
from app.api.v1.auth import auth
from app.models import User, Post, Role
from .errors import forbidden, something_wrong, UserValidateError, error_404
from app.api.decorators import permission_required

@api_v1.before_request
@auth.login_required
#@permission_required(63)
def before_request():
    pass

@api_v1.errorhandler(UserValidateError)
def user_validate_error(e):
    return something_wrong(e.args[0])

@api_v1.errorhandler(404)
def api_404(e):
    return error_404('请求的资源不存在')

@api_v1.after_request
def __after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Authorization')
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
        return {'posts': [post.to_json() for post in [posts]], 'content': posts.body_md}
    else:
        posts = Post.query.all()
    return {'posts': [post.to_json() for post in list(posts) ]}

@api_v1.route('/get-role')
def get_role():
    _id = request.args.get('id')
    if _id:
        roles = Role.query.get(_id)
        if not roles:
            return something_wrong('查询的角色不存在')
        return {'roles': [role.to_json() for role in [roles]]}
    else:
        roles = Role.query.all()
    return {'roles': [role.to_json() for role in roles ]}

@api_v1.route('/edit-post/<int:id>')
def edit_post(id):
    if not g.current_user.can(63):
        return forbidden('没有权限')
    _todo = request.args.get('todo')
    _post = Post.query.get_or_404(id)
    _statue = ''
    if _todo == 'privacy' and request.method == 'GET':
        _post.is_public = not _post.is_public
        _statue = '私密'+ str(_post.is_public)
        db.session.add(_post)
    elif _todo == 'delete' and request.method == 'GET':
        db.session.delete(_post)
        _statue = '删除成功'
    else:
        return something_wrong('未知的请求')
    try:
        db.session.commit()
        return jsonify({'message': '操作'+_todo+'成功', 'status': _statue}), 200
    except Exception:
        return jsonify({'message': '操作失败'})

@api_v1.route('/test')
def ap1_test():
    def lalala():
        import time
        with open(r'D:\pycharm\project\project_demo\end\app\static\css\bootstrap-icons.css') as f:
            char = f.read(1)
            while char:
                yield char
                char = f.read(1)
    return lalala(), 200