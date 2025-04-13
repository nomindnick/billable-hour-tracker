# tests/test_calculations.py
import unittest
from datetime import date
from app.calculations.workdays import (
    is_weekend, get_workdays_in_year, get_workdays_by_month
)
from app.calculations.distribution import (
    distribute_hours_by_month, calculate_daily_targets
)
from app.calculations.service import BillableHourCalculationService

class TestWorkdays(unittest.TestCase):
    """Tests for workday calculation functions."""
    
    def test_is_weekend(self):
        """Test weekend detection."""
        # Monday (not a weekend)
        self.assertFalse(is_weekend(date(2025, 4, 7)))
        # Saturday (weekend)
        self.assertTrue(is_weekend(date(2025, 4, 12)))
        # Sunday (weekend)
        self.assertTrue(is_weekend(date(2025, 4, 13)))
    
    def test_get_workdays_in_year(self):
        """Test workday calculation for a year."""
        # For simplicity, we'll just check January 2025
        # January 2025 has 31 days, with 4 Saturdays and 4 Sundays
        # So it should have 31 - 8 = 23 workdays
        
        # Get all workdays in 2025
        workdays = get_workdays_in_year(2025)
        
        # Filter for January
        january_workdays = [day for day in workdays if day.month == 1]
        
        self.assertEqual(len(january_workdays), 23)
    
    def test_get_workdays_with_days_off(self):
        """Test workday calculation with days off."""
        # Define some days off (e.g., holidays in January 2025)
        days_off = [
            date(2025, 1, 1),  # New Year's Day
            date(2025, 1, 20)  # MLK Day
        ]
        
        # Get workdays with days off
        workdays = get_workdays_in_year(2025, days_off)
        
        # Days off should not be in workdays
        self.assertNotIn(date(2025, 1, 1), workdays)
        self.assertNotIn(date(2025, 1, 20), workdays)
        
        # Filter for January
        january_workdays = [day for day in workdays if day.month == 1]
        
        # Should be 23 - 2 = 21 workdays in January
        self.assertEqual(len(january_workdays), 21)
    
    def test_get_workdays_by_month(self):
        """Test getting workday counts by month."""
        workdays_by_month = get_workdays_by_month(2025)
        
        # January 2025 should have 23 workdays
        self.assertEqual(workdays_by_month[1], 23)
        
        # Total should be roughly 260-262 workdays in a year (52 weeks × 5 days)
        total_workdays = sum(workdays_by_month.values())
        self.assertTrue(260 <= total_workdays <= 262)

class TestDistribution(unittest.TestCase):
    """Tests for billable hour distribution functions."""
    
    def test_distribute_hours_by_month(self):
        """Test distribution of hours across months."""
        # Create a simple test case with equal workdays per month
        workdays_by_month = {month: 20 for month in range(1, 13)}
        
        # Test with even distribution (no weights)
        hours_by_month = distribute_hours_by_month(2000, workdays_by_month)
        
        # Each month should get 1/12 of total hours
        for month, hours in hours_by_month.items():
            self.assertAlmostEqual(hours, 2000 / 12)
        
        # Test with weighted distribution
        monthly_weights = {
            1: 1.2,  # January is 20% busier
            7: 0.8,  # July is 20% slower
        }
        
        hours_by_month = distribute_hours_by_month(
            2000, workdays_by_month, monthly_weights
        )
        
        # January should get more hours than equal distribution
        self.assertTrue(hours_by_month[1] > 2000 / 12)
        
        # July should get fewer hours than equal distribution
        self.assertTrue(hours_by_month[7] < 2000 / 12)
        
        # Total should still be 2000
        self.assertAlmostEqual(sum(hours_by_month.values()), 2000)
    
    def test_calculate_daily_targets(self):
        """Test calculation of daily targets."""
        # Simple test case: one month with even distribution
        hours_by_month = {1: 100}  # 100 hours in January
        
        # Create 20 workdays in January
        january_dates = [date(2025, 1, day) for day in range(6, 26)]
        workday_dates_by_month = {1: january_dates}
        
        # Calculate daily targets
        daily_targets = calculate_daily_targets(hours_by_month, workday_dates_by_month)
        
        # Each day should get 5 hours
        for day, hours in daily_targets.items():
            self.assertAlmostEqual(hours, 5.0)
        
        # Test with max_daily_hours constraint
        hours_by_month = {1: 300}  # 300 hours in January (15 per day)
        daily_targets = calculate_daily_targets(
            hours_by_month, workday_dates_by_month, max_daily_hours=10.0
        )
        
        # Each day should be capped at 10 hours
        for day, hours in daily_targets.items():
            self.assertLessEqual(hours, 10.0)
        
        # Only 200 hours would be allocated (10 hours × 20 days)
        self.assertAlmostEqual(sum(daily_targets.values()), 200.0)

class TestCalculationService(unittest.TestCase):
    """Tests for the billable hour calculation service."""
    
    def test_generate_plan(self):
        """Test generation of a complete plan."""
        service = BillableHourCalculationService(max_daily_hours=8.0)
        
        # Create a simple test case
        year = 2025
        total_hours = 2000
        days_off = [
            date(2025, 1, 1),  # New Year's Day
            date(2025, 12, 25)  # Christmas
        ]
        monthly_weights = {
            1: 1.0,  # January: normal
            6: 0.8,  # June: 20% slower
            12: 1.2  # December: 20% busier
        }
        
        # Generate plan
        plan = service.generate_plan(
            year, total_hours, days_off, monthly_weights
        )
        
        # Check that we have a plan for workdays only (not weekends or days off)
        for day in plan.keys():
            self.assertFalse(is_weekend(day))
            self.assertNotIn(day, days_off)
        
        # Check that we respect max_daily_hours
        for hours in plan.values():
            self.assertLessEqual(hours, 8.0)
        
        # Check that total planned hours equals the goal
        planned_hours = sum(plan.values())
        # Allow for some floating-point variance
        self.assertAlmostEqual(planned_hours, total_hours, delta=0.5)
    
    def test_get_monthly_summary(self):
        """Test generation of monthly summary."""
        service = BillableHourCalculationService()
        
        # Create a simple plan
        daily_targets = {
            date(2025, 1, 5): 5.0,
            date(2025, 1, 6): 6.0,
            date(2025, 2, 3): 7.0,
            date(2025, 2, 4): 8.0
        }
        
        # Get monthly summary
        monthly_summary = service.get_monthly_summary(daily_targets)
        
        self.assertEqual(monthly_summary[1], 11.0)  # January: 5 + 6 = 11
        self.assertEqual(monthly_summary[2], 15.0)  # February: 7 + 8 = 15
        self.assertEqual(monthly_summary[3], 0.0)   # March: no days
        
    def test_calculate_progress_metrics(self):
        """Test calculation of progress metrics."""
        service = BillableHourCalculationService()
        
        # Set up test data
        goal_hours = 2000
        daily_targets = {
            date(2025, 1, 5): 8.0,
            date(2025, 1, 6): 8.0,
            date(2025, 1, 7): 8.0,
            date(2025, 1, 8): 8.0,
            date(2025, 1, 9): 8.0,
            # Future dates
            date(2025, 1, 12): 8.0,
            date(2025, 1, 13): 8.0,
        }
        
        logged_hours = {
            date(2025, 1, 5): 9.0,  # Over target
            date(2025, 1, 6): 7.0,  # Under target
            date(2025, 1, 7): 8.0,  # On target
            date(2025, 1, 8): 6.0,  # Under target
            # Missing day (1/9)
        }
        
        # Mock today's date for testing
        # Patching date.today() would be better but requires more setup
        original_today = date.today
        try:
            date.today = lambda: date(2025, 1, 9)
            
            metrics = service.calculate_progress_metrics(
                goal_hours, daily_targets, logged_hours
            )
            
            # Total logged should be sum of logged_hours
            self.assertEqual(metrics['total_logged'], 30.0)  # 9 + 7 + 8 + 6
            
            # Target to date should be sum of targets through today
            self.assertEqual(metrics['target_to_date'], 40.0)  # 5 days * 8 hours
            
            # Current pace should be total_logged - target_to_date
            self.assertEqual(metrics['current_pace'], -10.0)  # 10 hours behind
            
            # Remaining workdays should be days after today
            self.assertEqual(metrics['remaining_workdays'], 2)  # 1/12 and 1/13
            
            # Remaining target should be goal_hours - total_logged
            self.assertEqual(metrics['remaining_target'], 1970.0)  # 2000 - 30
            
            # Recommended daily should be remaining_target / remaining_workdays
            self.assertEqual(metrics['recommended_daily'], 985.0)  # 1970 / 2
            
        finally:
            # Restore original date.today
            date.today = original_today


if __name__ == '__main__':
    unittest.main()