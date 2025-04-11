# app/models.py
from app import db # Import the db instance from app/__init__.py

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    # We'll store hashed passwords, not plaintext
    password_hash = db.Column(db.String(128), nullable=False) # Increased length for bcrypt

    def __repr__(self):
        return f'<User {self.email}>'

    # Add methods for setting/checking password later (Sprint 2)
    # def set_password(self, password):
    #     pass # To be implemented
    # def check_password(self, password):
    #     pass # To be implemented