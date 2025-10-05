from flask import Blueprint

routes_bp = Blueprint('routes', __name__)

from . import login_routes, auditoires_routes, presence_routes