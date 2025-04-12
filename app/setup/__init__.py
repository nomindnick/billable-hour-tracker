# app/setup/__init__.py
from flask import Blueprint

bp = Blueprint('setup', __name__)

# Import routes at the bottom to avoid circular dependencies
from app.setup import routes