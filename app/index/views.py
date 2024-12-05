import typing

from flask import render_template, request, current_app

from app.index import index
from app.models import Permission, Post, Category

if typing.TYPE_CHECKING:
    from flask_sqlalchemy.pagination import Pagination
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
    posts:_posts = Post.query.order_by(Post.date.desc()).paginate(page=page,
                                                                  per_page=current_app.config['POSTS_PER_PAGE'],
                                                                  max_per_page=current_app.config['POSTS_PER_PAGE'],
                                                                  error_out=True)
    categories = Category.query.all()
    _struct = {}
    # for i in categories:
    #     _struct[i.name] =[l.title for l in i.posts.all()]
    return render_template('index/homepage.html', posts = posts.items, categories = categories, _struct = _struct, pagination = posts)