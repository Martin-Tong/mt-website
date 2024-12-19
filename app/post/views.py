from flask import render_template, redirect, url_for, jsonify, abort
from flask_login import login_required, current_user

from app import db
from app.models import Post, Category
from app.post import post
from app.post.forms import PublishForm
from app.utils import my_flash
from app.decorators import header_required

@post.route('/publish', methods=['GET', 'POST'])
@login_required
def publish():
    form = PublishForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.content.data
        category = form.category.data
        is_public = form.is_public.data
        if category == '未分类':
            category = None
        else:
            category= Category.query.filter_by(name = category).first()
            print(is_public)
        _post  = Post(title = title, body_md = body, category = category, author = current_user._get_current_object(), is_public= is_public)
        db.session.add(_post)
        db.session.commit()
        my_flash('发表成功', 'success')
        return redirect(url_for('post.post_detail', id = _post.id))
    return render_template('post/publish.html', form = form)

@post.route('/<int:id>')
def post_detail(id):
    _post = Post.query.get_or_404(id)
    if _post.is_public == True and current_user.id != _post.author.id:
        abort(403, {'message':'私密文章'})
    return render_template('post/preview.html', post=_post)

@post.route('/category/<string:category>')
def post_category(category):
    pass


@post.route('/<int:id>/edit', methods = ['GET', 'POST'])
@login_required
def post_edit(id):
    _post = Post.query.get_or_404(id)
    if current_user.id == _post.author.id or current_user.can(31) :
        form = PublishForm()
        if form.validate_on_submit():
            _post.title = form.title.data
            _post.body_md = form.content.data
            _post.is_public = form.is_public.data
            if form.category.data == '未分类':
                _post.category = None
            else:
                category = Category.query.filter_by(name=form.category.data).first()
                _post.category = category
            db.session.add(_post)
            db.session.commit()
            my_flash('编辑成功', 'success')
            return redirect(url_for('post.post_detail', id=_post.id))
        form.title.data = _post.title
        form.content.data = _post.body_md
        form.is_public.data = _post.is_public
        if _post.category:
            form.category.data = _post.category.name
        else:
            form.category.data = '未分类'
        return render_template('post/reedit.html', form = form)
    abort(403)


@post.route('/<int:id>/delete')
@header_required('N-From-Fetch')
def post_delete(id):
    if not current_user.is_authenticated:
        return jsonify({'message':'用户未登录'})
    _post = Post.query.get_or_404(id)
    if current_user.id == _post.author.id or current_user.can(31):
        try:
            db.session.delete(_post)
            db.session.commit()
            return jsonify({'message':'文章删除成功'})
        except Exception:
            return jsonify({'message':'删除失败，请检查参数后重试'})
    return jsonify({'message': '没有删除权限'})