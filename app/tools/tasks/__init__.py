from celery import shared_task
from flask import current_app
from app.models import User
import typing

if typing.TYPE_CHECKING:
    from redis import Redis
    _redis = Redis

@shared_task
def ask_for_confirm(db):
    user_needs_confirm = User.query.filter_by(confirmed = False).all()
    redis:_redis = current_app.extensions['redis'](db)
    for index,value in enumerate(user_needs_confirm):
        redis.hset(value.id, 'confirmed', value.confirmed)