from flask import render_template, redirect, url_for
from flask_login import login_required, current_user

from app import db
from app.models import Post, Category
from app.post import post
from app.post.forms import PublishForm
from app.utils import my_flash


@post.route('/publish', methods=['GET', 'POST'])
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
        _post  = Post(title = title, body_md = body, category = category, author = current_user._get_current_object())
        db.session.add(_post)
        db.session.commit()
        my_flash('发表成功', 'success')
        return redirect(url_for('post.post_detail', id = _post.id))
    return render_template('post/publish.html', form = form)

@post.route('/<int:id>')
def post_detail(id):
    _post = Post.query.get_or_404(id)
    return render_template('post/preview.html', post=_post)

@post.route('/category/<string:category>')
def post_category(category):
    pass


@post.route('/<int:id>/edit')
def post_edit(id):
    pass

@post.route('/<int:id>/delete')
def post_delete(id):
    pass