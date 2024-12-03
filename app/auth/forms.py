from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, length, Regexp, EqualTo, ValidationError

from app.models import User


class LoginForm(FlaskForm):
    name = StringField('用户名/邮箱', [DataRequired(), length(8)])
    password = PasswordField('密码', [DataRequired()])
    remember_me = BooleanField('记住我（下次自动登录）',name='checkbox')
    submit = SubmitField('登录')

class RegisterForm(FlaskForm):
    username = StringField('用户名', [DataRequired(), length(6,15, message='用户名长度为6-15个字符'), Regexp('^[a-zA-Z][0-9a-zA-Z_.]*$', message='用户名必须以字母开头，只能包含字母数字_.')])
    email = StringField('邮箱', [DataRequired(), length(6, message='邮箱长度异常'), Email('非法的邮箱地址')])
    password = PasswordField('密码', validators=[DataRequired('密码不能为空'), length(8, 15 ,message='密码长度为8-15个字符')])
    password2 = PasswordField('确认密码', [EqualTo('password', '两次输入的密码不一致')])
    submit = SubmitField('注册')

    def validate_username(self, field):
        if User.query.filter_by(username = field.data).first():
            raise ValidationError('用户名已存在')

    def validate_email(self, field):
        if User.query.filter_by(email = field.data).first():
            raise ValidationError('邮箱已注册')
