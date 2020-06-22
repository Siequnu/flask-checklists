from flask import Blueprint

bp = Blueprint('checklists', __name__, template_folder = 'templates')

from . import routes, models