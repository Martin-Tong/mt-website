from app.index import index
from flask import render_template
from app.email import send_mail
from flask_login import current_user

@index.route('/')
def homepage():
    return render_template('homepage.html')