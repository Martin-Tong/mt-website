from app.message import message
from flask import render_template, current_app
from flask_login import login_required, current_user


@message.route('/')
@login_required
def message():
    redis = current_app.extensions['redis'](2)
    id = str(current_user.id)
    try:
        if redis.exists(id):
            result = redis.hgetall(id)
            return render_template('message/index.html', data=result, enumerate=enumerate)
    except Exception as e:
        pass
    return render_template('message/index.html')
