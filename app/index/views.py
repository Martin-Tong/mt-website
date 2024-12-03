from flask import render_template, make_response, redirect, url_for
from flask_login import login_required, current_user

from app.index import index
from app.index.forms import PublishForm
from app.models import Permission, Post, Category

from app import db
from app.utils import my_flash


# @index.after_app_request
# def remove_server_header(response):
#     response.headers.pop('server', None)
#     print(response.headers)
#     return response
@index.app_context_processor
def define_permission_context():
    return dict(Permission = Permission)

@index.route('/publish', methods=['GET', 'POST'])
@login_required
def publish():
    form = PublishForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.content.data
        category = form.category.data
        if category == '未分类':
            category = None
        else:
            category= Category.query.filter_by(name = category).first()
        post  = Post(title = title, body_md = body, category = category, author = current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        my_flash('发表成功', 'success')
        return redirect(url_for('post.post_detail', id = post.id))
    return render_template('post/publish.html', form = form)

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