from flask import render_template, url_for, redirect
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.auth import auth
from app.auth.forms import *
from app.models import User
from app.utils import my_flash
from app.email import send_mail

@auth.route('/about/<user_name>')
@login_required
def _aboutme(user_name):
    user = User.query.filter_by(username = user_name).first_or_404('未查询到用户')
    return render_template('auth/aboutme.html', user = user)

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
        return redirect(url_for('._login',_method='GET'))
    return render_template('auth/login.html', form = form)


@auth.route('/register', methods = ['GET', 'POST'])
def _register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.username.data
        mail = form.email.data
        passwd = form.password.data

        user = User(username = name, email = mail, password = passwd)
        db.session.add(user)
        db.session.commit()
        token = user.generate_validate_token()
        send_mail(mail, '请确认你在NOC注册的邮箱地址', 'email/confirm', token = token, user = user)
        my_flash('注册成功，一个确认邮件已经发到你的注册邮箱地址，请前往确认', 'success')
        return redirect(url_for('._login'))
    return render_template('auth/register.html', form = form)

@auth.route('/logout')
@login_required
def _logout():
    logout_user()
    my_flash('用户已登出', 'success')
    return redirect(url_for('index.homepage'))


@auth.route('/confirm/<token>')
@login_required
def _confirm(token):
    if current_user.confirmed:
        return redirect(url_for('index.homepage'))
    if current_user.confirm(token):
        db.session.commit()
        my_flash('邮箱验证成功', 'success')
    else:
        my_flash('链接已过期或链接不一致，请重新发起验证', 'danger')
    return redirect(url_for('index.homepage'))


def validate_username_or_email(data):
    if data.find('@') > -1:
        return {'email': data}
    return {'username': data}