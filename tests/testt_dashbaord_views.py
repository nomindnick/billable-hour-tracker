# tests/test_dashboard_views.py
import unittest
from datetime import date
from flask import url_for
from app import create_app, db
from app.models import User, Goal, DayOff, MonthlyWeight, DailyLog

class TestDashboardViews(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Create test user
        user = User(email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        
        # Create goal
        goal = Goal(user_id=1, year=2025, total_hours=2000)
        db.session.add(goal)
        
        # Create monthly weights
        for month in range(1, 13):
            weight = 1.0
            if month == 6:  # June is slower
                weight = 0.8
            if month == 12:  # December is busier
                weight = 1.2
            monthly_weight = MonthlyWeight(
                user_id=1, year=2025, month=month, weight=weight
            )
            db.session.add(monthly_weight)
        
        # Create some days off
        days_off = [
            DayOff(user_id=1, date=date(2025, 1, 1), type='Holiday'),  # New Year's
            DayOff(user_id=1, date=date(2025, 12, 25), type='Holiday')  # Christmas
        ]
        for day_off in days_off:
            db.session.add(day_off)
        
        # Create some daily logs
        logs = [
            DailyLog(user_id=1, date=date(2025, 1, 5), hours_billed=8.5),
            DailyLog(user_id=1, date=date(2025, 1, 6), hours_billed=7.0)
        ]
        for log in logs:
            db.session.add(log)
        
        db.session.commit()
        
        # Log in the test user
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'test@example.com', 'password': 'password'},
                follow_redirects=True
            )
    
    def tearDown(self):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_dashboard_access(self):
        """Test that authenticated users can access the dashboard."""
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
    
    def test_calendar_view(self):
        """Test the calendar view."""
        response = self.client.get('/dashboard/calendar')
        self.assertEqual(response.status_code, 200)
        
        # Test with specific month and year
        response = self.client.get('/dashboard/calendar?month=6&year=2025')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'June', response.data)  # Should contain month name
    
    def test_log_hours(self):
        """Test the log hours functionality."""
        # Test GET (form display)
        response = self.client.get('/dashboard/log_hours')
        self.assertEqual(response.status_code, 200)
        
        # Test POST (submit form)
        response = self.client.post(
            '/dashboard/log_hours',
            data={'date': '2025-01-10', 'hours': 7.5},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify the log was saved
        log = DailyLog.query.filter_by(
            user_id=1, date=date(2025, 1, 10)
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.hours_billed, 7.5)
    
    def test_update_existing_log(self):
        """Test updating an existing log."""
        # The log for Jan 5 was created in setUp with 8.5 hours
        response = self.client.post(
            '/dashboard/log_hours',
            data={'date': '2025-01-05', 'hours': 9.0},  # Change to 9.0
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify the log was updated
        log = DailyLog.query.filter_by(
            user_id=1, date=date(2025, 1, 5)
        ).first()
        self.assertEqual(log.hours_billed, 9.0)

if __name__ == '__main__':
    unittest.main()