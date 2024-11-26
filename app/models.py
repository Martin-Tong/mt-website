from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from app import db, login_manager
from flask import current_app

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, index = True)
    email = db.Column(db.String(64), unique = True, index = True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default = False)

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
        except SignatureExpired as e:
            return False
        if data['user'] != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def __repr__(self):
        return f'<User {self.username}>'

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)
    users = db.relationship(User, backref = 'role')

    def __repr__(self):
        return f'<Role {self.name}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

a=URLSafeTimedSerializer('test')
print(a.dumps({'name':1}))