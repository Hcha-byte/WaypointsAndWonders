from flask import Blueprint

main_bp = Blueprint("main", __name__)

from . import routes  # import routes at the end to avoid circular imports
