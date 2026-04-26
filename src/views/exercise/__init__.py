from flask import Blueprint

exercise_bp = Blueprint('exercise', __name__, template_folder='templates')

from . import routes
