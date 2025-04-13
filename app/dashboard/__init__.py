# app/dashboard/__init__.py
from flask import Blueprint

bp = Blueprint('dashboard', __name__)

# Custom filter for month names
@bp.app_template_filter('month_name')
def month_name_filter(month_num):
    """Convert month number to name."""
    months = [
        '', 'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    return months[month_num]

# Import routes at the bottom to avoid circular dependencies
from app.dashboard import routes