from flask import Blueprint

index = Blueprint('index', __name__)

from app.index import errors, views
