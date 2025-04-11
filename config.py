# config.py
import os
from dotenv import load_dotenv

# Determine the base directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))
# Load environment variables from .env file
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Secret key for session management, CSRF protection
    # IMPORTANT: Load from environment variable in production!
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-should-really-change-this'

    # Database configuration
    # Use SQLite for local development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    # Disable modification tracking to save resources, unless needed
    SQLALCHEMY_TRACK_MODIFICATIONS = False