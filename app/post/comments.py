import json
import time
import typing

from flask import jsonify, current_app, request
from flask_login import current_user, login_required

from app import cache
from app.decorators import header_required
from app.post import post

if typing.TYPE_CHECKING:
    from redis import Redis


def make_get_post_comments_key(id):
    return f'noc-post-{id}-comments'


@post.get('/<int:id>/comments')
@header_required('N-From-Fetch')
@cache.cached(timeout=30, make_cache_key=make_get_post_comments_key)
def get_post_comments(id):
    redis: Redis = current_app.extensions['redis'](4)
    comments = redis.lrange(f'post-{id}-comments', 0, -1)
    comments = {'comments': [json.loads(comment) for comment in comments]}
    return jsonify(comments)


@post.post('/<int:id>/comments')
@login_required
@header_required('N-From-Fetch')
def set_post_comments(id):
    redis: Redis = current_app.extensions['redis'](4)
    try:
        comment_id = redis.incr('comment_id')
        redis.lpush(f'post-{id}-comments', json.dumps({
            'content': request.json.get('comments'),
            'time': time.time(),
            'author': current_user.username,
            'post': id,
            'id': comment_id
        }))
        return {'status': 'success', 'message': '评论成功'}
    except Exception:
        return {'status': 'error', 'message': '评论失败'}


@post.delete('/<int:id>/comments')
@login_required
@header_required('N-From-Fetch')
def delete_post_comments(id):
    redis: Redis = current_app.extensions['redis'](4)
    try:
        redis.decr('comment_id')
        redis.lrem(f'post-{id}-comments', 0, json.dumps({
            'content': request.json.get('comments'),
            'time': request.json.get('time'),
            'author': current_user.username,
            'post': id,
            'id': request.json.get('id')
        }))
        return {'status': 'success', 'message': '删除评论成功'}
    except Exception:
        return {'status': 'error', 'message': '删除评论失败'}
