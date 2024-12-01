from flask import render_template, make_response

from app.index import index
from app.models import Permission, Post, Category

# @index.after_app_request
# def remove_server_header(response):
#     response.headers.pop('server', None)
#     print(response.headers)
#     return response
@index.app_context_processor
def define_permission_context():
    return dict(Permission = Permission)

@index.route('/')
def homepage():
    posts = Post.query.all()
    categories = Category.query.all()
    _struct = {}
    for i in categories:
        _struct[i.name] =[l.title for l in i.posts.all()]
    #_struct = json.dumps(_struct)
    a= make_response(render_template('index/homepage.html', posts = posts, categories = categories, _struct = _struct))

    return a