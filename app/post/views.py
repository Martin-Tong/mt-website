from flask import render_template

from app.models import Post
from app.post import post


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