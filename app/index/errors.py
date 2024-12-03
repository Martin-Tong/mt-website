from flask import render_template
from app.index import index

@index.app_errorhandler(404)
def e_404(e):
    return render_template('404.html')

@index.app_errorhandler(500)
def e_500(e):
    return render_template('500.html')