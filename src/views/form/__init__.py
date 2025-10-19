from flask import Blueprint

form_bp = Blueprint(
    'form',
    __name__
)

from . import routes