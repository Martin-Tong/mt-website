from flask import Blueprint

message = Blueprint('message', __name__)

from app.message import views
