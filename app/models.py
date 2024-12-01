import typing
from datetime import datetime
import re
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
            'Admin': [Permission.FOLLOW, Permission.ADMIN, Permission.PUBLIC, Permission.COMMENT, Permission.SUPERVISOR]
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

    @staticmethod
    def insert_categories(data:str|list[str]) -> None:
        if type(data) == str:
            data = [data]
        for i in data:
            if not Category.query.filter_by(name = i).first():
                db.session.add(Category(name = i))
        db.session.commit()

    def __repr__(self):
        return f'<Category {self.name}>'

class Permission:
    COMMENT = 1 #评论权限
    FOLLOW = 2 #关注他人权限
    PUBLIC = 4 #发表文章权限
    SUPERVISOR = 8 #协助管理权限
    ADMIN = 16 #管理权限

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
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.Linker(url_re=re.compile('^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$'),
                                         email_re=re.compile('^([\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+)$'),
                                         parse_email=True, skip_tags={'pre', 'code'}).linkify(bleach.clean(markdown(value, output_format='html'),
                                                                                                           tags = safe_tags, strip=True))

db.event.listen(Post.body_md, 'set', Post.on_change_body_md)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
