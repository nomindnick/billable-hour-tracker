# app/main/routes.py
from flask import render_template
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    # We can pass variables to the template later
    user = {'username': 'New User'} # Example data
    return render_template('index.html', title='Home', user=user)