# app/models.py
from datetime import date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Relationships
    goals = db.relationship('Goal', backref='user', lazy='dynamic')
    days_off = db.relationship('DayOff', backref='user', lazy='dynamic')
    monthly_weights = db.relationship('MonthlyWeight', backref='user', lazy='dynamic')
    daily_logs = db.relationship('DailyLog', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        """Create hashed password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password"""
        return check_password_hash(self.password_hash, password)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_hours = db.Column(db.Integer, nullable=False)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'year'),)
    
    def __repr__(self):
        return f'<Goal {self.year}: {self.total_hours} hours>'

class DayOff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(20), nullable=True)  # 'Holiday', 'Vacation', 'Personal'
    
    __table_args__ = (db.UniqueConstraint('user_id', 'date'),)
    
    def __repr__(self):
        return f'<DayOff {self.date}: {self.type}>'

class MonthlyWeight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False) 
    month = db.Column(db.Integer, nullable=False)  # 1-12
    weight = db.Column(db.Float, nullable=False, default=1.0)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'year', 'month'),)
    
    def __repr__(self):
        return f'<MonthlyWeight {self.year}-{self.month}: {self.weight}>'

class DailyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hours_billed = db.Column(db.Float, nullable=False)
    target_hours_override = db.Column(db.Float, nullable=True)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'date'),)
    
    def __repr__(self):
        return f'<DailyLog {self.date}: {self.hours_billed} hours>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))