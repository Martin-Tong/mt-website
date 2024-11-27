from flask import Flask
from flask_login import LoginManager
# from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from config import config as configmap

#bootstrap: Bootstrap = Bootstrap()
db: SQLAlchemy = SQLAlchemy()
mail: Mail = Mail()
moment: Moment = Moment()
login_manager: LoginManager = LoginManager()
login_manager.login_view = 'auth._login'
login_manager.login_message = '该页面/功能需要登录'
login_manager.login_message_category = 'danger'

from app.models import AnonymousUser
login_manager.anonymous_user = AnonymousUser


def create_app(_config='default'):
    app = Flask(__name__)
    app.config.from_object(configmap[_config])
    configmap[_config].init_app(app)

    #bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)

    #注册蓝图
    from .index import index as index_blueprint
    app.register_blueprint(index_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix = '/auth')

    return app
