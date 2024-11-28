#from werkzeug.datastructures import MultiDict
from flask import render_template, make_response

from app.index import index
from app.models import Permission


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
    a= make_response(render_template('index/homepage.html'))
    #a.headers.update(MultiDict([('server', 'test')]))
    return a