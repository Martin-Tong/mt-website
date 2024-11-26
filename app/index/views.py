from app.index import index
from flask import render_template


@index.route('/')
def homepage():
    return render_template('homepage.html')