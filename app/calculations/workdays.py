# app/calculations/workdays.py
import calendar
from datetime import date, datetime, timedelta
from typing import List, Set, Dict

def is_weekend(day: date) -> bool:
    """Check if a date is a weekend (Saturday or Sunday)."""
    return day.weekday() >= 5  # 5 is Saturday, 6 is Sunday

def get_workdays_in_year(year: int, days_off: List[date] = None) -> List[date]:
    """
    Get all working days (excluding weekends and specified days off) in a year.
    
    Args:
        year: The year to calculate workdays for
        days_off: List of dates to exclude (holidays, vacation, etc.)
        
    Returns:
        List of dates that are working days
    """
    if days_off is None:
        days_off = []
    
    # Convert days_off to a set for faster lookups
    days_off_set = set(days_off)
    
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    # Generate all days in the year
    workdays = []
    current_date = start_date
    while current_date <= end_date:
        # If it's not a weekend and not in days_off, it's a workday
        if not is_weekend(current_date) and current_date not in days_off_set:
            workdays.append(current_date)
        
        current_date += timedelta(days=1)
    
    return workdays

def get_workdays_by_month(year: int, days_off: List[date] = None) -> Dict[int, int]:
    """
    Get the number of working days for each month in a year.
    
    Args:
        year: The year to calculate for
        days_off: List of dates to exclude (holidays, vacation, etc.)
        
    Returns:
        Dictionary with month number (1-12) as key and number of workdays as value
    """
    workdays = get_workdays_in_year(year, days_off)
    
    # Count workdays per month
    workdays_by_month = {month: 0 for month in range(1, 13)}
    for day in workdays:
        workdays_by_month[day.month] += 1
    
    return workdays_by_month

def get_workday_dates_by_month(year: int, days_off: List[date] = None) -> Dict[int, List[date]]:
    """
    Get the actual workday dates for each month in a year.
    
    Args:
        year: The year to calculate for
        days_off: List of dates to exclude (holidays, vacation, etc.)
        
    Returns:
        Dictionary with month number (1-12) as key and list of workday dates as value
    """
    workdays = get_workdays_in_year(year, days_off)
    
    # Group workdays by month
    workday_dates_by_month = {month: [] for month in range(1, 13)}
    for day in workdays:
        workday_dates_by_month[day.month].append(day)
    
    return workday_dates_by_month