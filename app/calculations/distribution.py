# app/calculations/distribution.py
from datetime import date
from typing import Dict, List, Optional

def distribute_hours_by_month(
    total_hours: int, 
    workdays_by_month: Dict[int, int], 
    monthly_weights: Dict[int, float] = None
) -> Dict[int, float]:
    """
    Distribute total billable hours across months based on working days and weights.
    
    Args:
        total_hours: Annual billable hour goal
        workdays_by_month: Dictionary with month number as key and workday count as value
        monthly_weights: Dictionary with month number as key and weight as value (default: all 1.0)
        
    Returns:
        Dictionary with month number as key and allocated hours as value
    """
    if monthly_weights is None:
        monthly_weights = {month: 1.0 for month in range(1, 13)}
    
    # Calculate weighted workdays
    weighted_workdays = {}
    total_weighted_workdays = 0
    
    for month in range(1, 13):
        weight = monthly_weights.get(month, 1.0)
        workdays = workdays_by_month.get(month, 0)
        weighted_workdays[month] = workdays * weight
        total_weighted_workdays += weighted_workdays[month]
    
    # Distribute total hours proportionally
    hours_by_month = {}
    for month in range(1, 13):
        if total_weighted_workdays > 0:
            proportion = weighted_workdays[month] / total_weighted_workdays
            hours_by_month[month] = total_hours * proportion
        else:
            hours_by_month[month] = 0
    
    return hours_by_month

def calculate_daily_targets(
    hours_by_month: Dict[int, float], 
    workday_dates_by_month: Dict[int, List[date]],
    max_daily_hours: float = 10.0
) -> Dict[date, float]:
    """
    Calculate target billable hours for each workday.
    
    Args:
        hours_by_month: Dictionary with month number as key and allocated hours as value
        workday_dates_by_month: Dictionary with month number as key and list of workday dates as value
        max_daily_hours: Maximum target hours per day (to avoid unrealistic targets)
        
    Returns:
        Dictionary with date as key and target hours as value
    """
    daily_targets = {}
    excess_hours = 0  # Track hours that exceed max_daily_hours
    
    # First pass: Distribute hours evenly within each month
    for month in range(1, 13):
        month_hours = hours_by_month.get(month, 0)
        workdays = workday_dates_by_month.get(month, [])
        
        if not workdays:
            continue
        
        hours_per_day = month_hours / len(workdays)
        
        # If hours per day exceeds max, track the excess for redistribution
        if hours_per_day > max_daily_hours:
            excess_in_month = (hours_per_day - max_daily_hours) * len(workdays)
            excess_hours += excess_in_month
            hours_per_day = max_daily_hours
        
        for day in workdays:
            daily_targets[day] = hours_per_day
    
    # Second pass: Redistribute excess hours if needed
    if excess_hours > 0:
        # Find days with target below max
        available_days = []
        for day, hours in daily_targets.items():
            if hours < max_daily_hours:
                available_days.append(day)
        
        # Sort available days by date (earlier dates first)
        available_days.sort()
        
        # Redistribute excess hours
        if available_days:
            additional_per_day = min(
                (max_daily_hours - daily_targets[available_days[0]]),
                excess_hours / len(available_days)
            )
            
            for day in available_days:
                current_target = daily_targets[day]
                new_target = min(current_target + additional_per_day, max_daily_hours)
                daily_targets[day] = new_target
                excess_hours -= (new_target - current_target)
                
                if excess_hours <= 0:
                    break
    
    return daily_targets