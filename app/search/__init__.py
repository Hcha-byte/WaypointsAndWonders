from flask import Blueprint

search_bp = Blueprint("search", __name__)

from . import routes  # import routes at the end to avoid circular imports
