# run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Use Flask's development server
    # Debug=True enables auto-reloading and detailed error pages
    # IMPORTANT: Never run with debug=True in production!
    app.run(debug=True)