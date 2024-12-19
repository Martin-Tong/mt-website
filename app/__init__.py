from flask import Flask
from flask_login import LoginManager
# from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy
from celery import Celery,Task
from config import config as configmap
from redis import Redis

#bootstrap: Bootstrap = Bootstrap()
db = SQLAlchemy()
mail: Mail = Mail()
moment: Moment = Moment()
pagedown: PageDown = PageDown()
login_manager: LoginManager = LoginManager()
login_manager.login_view = 'auth._login'
login_manager.login_message = '该页面/功能需要登录'
login_manager.login_message_category = 'danger'

from app.models import AnonymousUser
login_manager.anonymous_user = AnonymousUser


def create_app(_config='default'):
    app = Flask(__name__)
    app.config.from_object(configmap[_config]())
    configmap[_config].init_app(app)

    #bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)
    login_manager.init_app(app)

    create_celery_app(app)
    create_redis(app)
    #注册蓝图
    from .index import index as index_blueprint
    app.register_blueprint(index_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix = '/user')

    from .post import post as post_blueprint
    app.register_blueprint(post_blueprint, url_prefix = '/post')

    from .api.v1 import api_v1 as a1
    app.register_blueprint(a1, url_prefix = '/ap1')

    return app

def create_celery_app(app:Flask):
    class FlaskTask(Task):
        """Create celery app."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.conf.broker_connection_retry_on_startup = True
    celery_app.conf.broker_url = app.config['CELERY_BROKER_URI']
    celery_app.conf.result_backend = app.config['CELERY_RESULT_BACKEND']
    celery_app.task_ignore_result = app.config['CELERY_TASK_IGNORE_RESULT']
    celery_app.conf.result_backend_transport_options = {
        'global_keyprefix':'noc'
    }
    celery_app.set_default()
    app.extensions['celery'] = celery_app

    return celery_app

def create_redis(app:Flask):
    def _redis(db):
        """Create redis app."""
        rd = Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'],
               password=app.config['REDIS_PASSWORD'], db=db, decode_responses=True)
        return rd
    app.extensions['redis'] = _redis
    return _redis