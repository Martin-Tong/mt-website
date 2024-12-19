import typing

from flask import render_template, request, current_app, jsonify

from app.index import index
from app.models import Permission, Post, Category
from app.decorators import header_required
from flask_login import login_required, current_user
import time

if typing.TYPE_CHECKING:
    from flask_sqlalchemy.pagination import Pagination
    from redis import Redis
    _redis = Redis
    _posts = Pagination

# @index.after_app_request
# def remove_server_header(response):
#     response.headers.pop('server', None)
#     print(response.headers)
#     return response
@index.app_context_processor
def define_permission_context():
    return dict(Permission = Permission)


@index.route('/', methods=['GET', 'POST'])
def homepage():
    page = request.args.get('page', 1, type=int)
    posts:_posts = Post.query.filter(Post.is_public != True).order_by(Post.date.desc()).paginate(page=page,
                                                                  per_page=current_app.config['POSTS_PER_PAGE'],
                                                                  max_per_page=current_app.config['POSTS_PER_PAGE'],
                                                            error_out=True)
    categories = Category.query.all()
    _struct = {}
    # for i in categories:
    #     _struct[i.name] =[l.title for l in i.posts.all()]
    return render_template('index/homepage.html', posts = posts.items, categories = categories, _struct = _struct, pagination = posts)

@index.route('/notice')
def notices():
    return render_template('/index/notices.html')


@index.route('/notices', methods=['GET'])
def get_notices():
    rd:_redis = current_app.extensions['redis'](1)
    keys = rd.keys('*')
    result = [rd.hgetall(i) for i in keys]
    return jsonify(result)


@index.post('/notices')
@login_required
@header_required('N-From-Fetch')
def add_notices():
    data = request.form.get('data')
    if data:
        _time = time.time()
        key = current_user.username +'-'+ str(_time)
        rd:_redis = current_app.extensions['redis'](1)
        try:
            rd.hset(key, mapping={'content':data, 'time': _time, 'key': key})
            rd.expire(key,60 * 60 * 24 * 3)
            return {'status': 'success'}
        except Exception as e:
            print(e)
            return {'status': 'error'}
    return {'status':'wrong'}