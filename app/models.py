import re
import typing
from datetime import datetime

import bleach
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

if typing.TYPE_CHECKING:
    import sqlalchemy as db
    # _db_type = typing.TypeVar('_db_type', bound=[
    #     typing.Optional[SQLAlchemy]
    # ])
    #db:_db_type


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, index = True)
    email = db.Column(db.String(64), unique = True, index = True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default = False)
    posts = db.relationship('Post', backref='author', lazy = 'dynamic')
    about_me = db.Column(db.String(128), nullable=True)
    register_date = db.Column(db.DateTime, default = datetime.today())


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['MAIL_ADMIN']:
                self.role = Role.query.filter_by(name = 'Admin').first()
            else:
                self.role = Role.query.filter_by(default = True).first()

    @property
    def password(self):
        raise AttributeError('用户密码不可明文展示！')

    @password.setter
    def password(self, data):
        self.password_hash = generate_password_hash(data)

    def validate_password(self, passwd):
        return check_password_hash(self.password_hash, passwd)

    def generate_validate_token(self):
        secret_key = current_app.config['SECRET_KEY']
        serializer = URLSafeTimedSerializer(secret_key)
        return serializer.dumps({'user': self.id}, 'register_confirmation')

    def confirm(self, token):
        serializer= URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token, 3600, salt='register_confirmation')
        except SignatureExpired:
            return False
        if data['user'] != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_api_token(self):
        secret_key = current_app.config['SECRET_KEY']
        serializer = URLSafeTimedSerializer(secret_key)
        return serializer.dumps({'user': self.id}, 'api_token')

    @staticmethod
    def varify_api_token(token):
        secret_key = current_app.config['SECRET_KEY']
        serializer = URLSafeTimedSerializer(secret_key)
        try:
            data = serializer.loads(token, 3600, salt='register_confirmation')
        except SignatureExpired:
            return False
        return User.query.get(data['user'])

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email' : self.email,
            'role': getattr(self.role, 'name', 'null'),
            'register_date': self.register_date.strftime('%Y-%m-%d %H:%M:%S'),
            'about_me': self.about_me,
            'confirmed': self.confirmed
        }

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_admin(self):
        return self.can('Admin')

    def __repr__(self):
        return f'<User {self.username}>'

class AnonymousUser(AnonymousUserMixin):
    def can(self):
        return False

    def is_admin(self):
        return False

class Permission:
    PUBLIC = 1 #发表文章权限
    COMMENT = 2 #评论权限
    FOLLOW = 4 #关注他人权限
    UPLOAD = 8 #上传文件权限
    SUPERVISOR = 16 #协助管理权限
    ADMIN = 32 #管理权限

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)
    default = db.Column(db.Boolean, default = False, index = True)
    permissions = db.Column(db.Integer)
    users = db.relationship(User, backref = 'role', lazy = 'dynamic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.permissions:
            self.permissions = 0

    #手动初始化所有用户角色
    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.PUBLIC, Permission.COMMENT],
            'Supervisor': [Permission.FOLLOW, Permission.COMMENT, Permission.PUBLIC, Permission.SUPERVISOR],
            'Admin': [Permission.FOLLOW, Permission.ADMIN, Permission.PUBLIC, Permission.COMMENT, Permission.SUPERVISOR, Permission.UPLOAD]
        }
        default_role = 'User'
        for r in roles:
            _r = Role.query.filter_by(name = r).first()
            if not _r:
                _r = Role(name = r)
            _r.reset_permission()
            for p in roles[r]:
                _r.add_permission(p)
            _r.default = (_r.name == default_role)
            db.session.add(_r)
        db.session.commit()


    def add_permission(self, data):
        if not self.has_permission(data):
            self.permissions += data

    def remove_permission(self, data):
        if self.has_permission(data):
            self.permissions -= data

    def reset_permission(self):
        self.permissions = 0

    def has_permission(self, data):
        return self.permissions & data == data

    def __repr__(self):
        return f'<Role {self.name}>'

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    posts = db.relationship('Post', backref='category', lazy='dynamic')

    #没有解耦，添加分类需要在category_list中添加后执行命令
    #同时需要在 app/index/forms.py 中同步修改
    @staticmethod
    def insert_categories() -> None:
        category_list = ['前端相关', 'Python', 'Nodejs', 'Flask中译']
        for i in category_list:
            if not Category.query.filter_by(name = i).first():
                db.session.add(Category(name = i))
        db.session.commit()

    @staticmethod
    def add_category(data):
        if not Category.query.filter_by(name=data).first():
            db.session.add(Category(name=data))
        db.session.commit()

    def __repr__(self):
        return f'<Category {self.name}>'

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(64), index = True)
    body_md = db.Column(db.Text)
    body_html = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.DateTime, index = True, default = datetime.today())
    last_modify = db.Column(db.DateTime)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    stars = db.Column(db.Integer, default=0)

    @staticmethod
    def on_change_body_md(target, value, oldvalue, initiator):
        safe_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'br']
        target.body_html = bleach.Linker(url_re=re.compile('^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$'),
                                         email_re=re.compile('^([\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+)$'),
                                         parse_email=True, skip_tags={'pre', 'code'}).linkify(bleach.clean(markdown(value, output_format='html'),
                                                                                                           tags = safe_tags, strip=True))

db.event.listen(Post.body_md, 'set', Post.on_change_body_md)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
