# app/calculations/service.py
from datetime import date
from typing import Dict, List, Optional

from app.calculations.workdays import get_workdays_by_month, get_workday_dates_by_month
from app.calculations.distribution import distribute_hours_by_month, calculate_daily_targets

class BillableHourCalculationService:
    """Service for calculating billable hour plans based on user inputs."""
    
    def __init__(self, max_daily_hours: float = 10.0):
        """
        Initialize the calculation service.
        
        Args:
            max_daily_hours: Maximum target hours per day (default: 10.0)
        """
        self.max_daily_hours = max_daily_hours
    
    def generate_plan(
        self, 
        year: int, 
        total_hours: int, 
        days_off: List[date] = None,
        monthly_weights: Dict[int, float] = None
    ) -> Dict[date, float]:
        """
        Generate a complete daily billable hour plan for the year.
        
        Args:
            year: The year to generate the plan for
            total_hours: Annual billable hour goal
            days_off: List of dates to exclude (holidays, vacation, etc.)
            monthly_weights: Dictionary with month number as key and weight as value
            
        Returns:
            Dictionary with date as key and target billable hours as value
        """
        # Get workdays counts and dates by month
        workdays_by_month = get_workdays_by_month(year, days_off)
        workday_dates_by_month = get_workday_dates_by_month(year, days_off)
        
        # Distribute hours across months
        hours_by_month = distribute_hours_by_month(
            total_hours, workdays_by_month, monthly_weights
        )
        
        # Calculate daily targets
        daily_targets = calculate_daily_targets(
            hours_by_month, workday_dates_by_month, self.max_daily_hours
        )
        
        return daily_targets
    
    def get_monthly_summary(self, daily_targets: Dict[date, float]) -> Dict[int, float]:
        """
        Calculate monthly totals from daily targets.
        
        Args:
            daily_targets: Dictionary with date as key and target hours as value
            
        Returns:
            Dictionary with month number as key and total hours as value
        """
        monthly_totals = {month: 0.0 for month in range(1, 13)}
        
        for day, hours in daily_targets.items():
            monthly_totals[day.month] += hours
        
        return monthly_totals
    
    def calculate_progress_metrics(
        self,
        goal_hours: int,
        daily_targets: Dict[date, float],
        logged_hours: Dict[date, float]
    ) -> Dict[str, float]:
        """
        Calculate progress metrics based on logged hours vs targets.
        
        Args:
            goal_hours: Annual billable hour goal
            daily_targets: Dictionary with date as key and target hours as value
            logged_hours: Dictionary with date as key and actual logged hours as value
        
        Returns:
            Dictionary with metrics (total_logged, target_to_date, current_pace, etc.)
        """
        today = date.today()
        
        # Calculate total logged hours
        total_logged = sum(logged_hours.values())
        
        # Calculate target to date (sum of targets for days that have passed)
        target_to_date = sum(hours for day, hours in daily_targets.items() if day <= today)
        
        # Calculate current pace (ahead or behind)
        current_pace = total_logged - target_to_date
        
        # Calculate recommended daily hours going forward
        remaining_workdays = [day for day in daily_targets.keys() if day > today]
        remaining_target = goal_hours - total_logged
        
        if remaining_workdays:
            recommended_daily = remaining_target / len(remaining_workdays)
        else:
            recommended_daily = 0
        
        return {
            'total_logged': total_logged,
            'target_to_date': target_to_date,
            'current_pace': current_pace,
            'remaining_workdays': len(remaining_workdays),
            'remaining_target': remaining_target,
            'recommended_daily': recommended_daily
        }