from flask import render_template, url_for, redirect

from app import db
from app.auth import auth
from app.auth.forms import *
from app.models import User
from app.utils import my_flash
from flask_login import login_user, logout_user, login_required


@auth.route('/')
@login_required
def _aboutme():
    return render_template('auth/aboutme.html')

@auth.route('/login', methods = ['GET', 'POST'])
def _login():
    form = LoginForm()
    if form.validate_on_submit():
        who = form.name.data
        who = validate_username_or_email(who)
        user = User.query.filter_by(**who).first()
        if user:
            if user.validate_password(form.password.data):
                login_user(user, form.remember_me.data)
                my_flash('登陆成功', 'success')
                return redirect(url_for('index.homepage'))
            else:
                my_flash('密码错误', 'danger')
        else:
            my_flash('用户不存在', 'warning')
        return redirect(url_for('._login'))
    return render_template('auth/login.html', form = form)


@auth.route('/register', methods = ['GET', 'POST'])
def _register():
    form = RegisterForm()
    my_flash('注册成功', 'success')
    if form.validate_on_submit():
        name = form.username.data
        mail = form.email.data
        passwd = form.password.data

        user = User(username = name, email = mail, password = passwd)
        db.session.add(user)
        db.session.commit()
        my_flash('注册成功', 'success')
        return redirect(url_for('._login'))
    return render_template('auth/register.html', form = form)

@auth.route('/logout')
@login_required
def _logout():
    logout_user()
    my_flash('用户已登出', 'success')
    return redirect(url_for('index.homepage'))


def validate_username_or_email(data):
    if data.find('@') > -1:
        return {'email': data}
    return {'username': data}