# app/dashboard/routes.py
from datetime import date
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required

from app import db
from app.dashboard import bp
from app.models import Goal, DayOff, MonthlyWeight, DailyLog
from app.calculations import BillableHourCalculationService

@bp.route('/')
@login_required
def index():
    """Display the user's dashboard."""
    # Get the current goal
    current_year = date.today().year
    goal = Goal.query.filter_by(user_id=current_user.id, year=current_year).first()
    
    if not goal:
        # Redirect to setup if no goal exists
        return render_template('dashboard/no_goal.html', year=current_year)
    
    # Get days off
    days_off = [day.date for day in DayOff.query.filter_by(user_id=current_user.id)]
    
    # Get monthly weights
    monthly_weights_db = MonthlyWeight.query.filter_by(user_id=current_user.id, year=current_year).all()
    monthly_weights = {mw.month: mw.weight for mw in monthly_weights_db}
    
    # Calculate plan
    calculation_service = BillableHourCalculationService()
    plan = calculation_service.generate_plan(
        current_year, goal.total_hours, days_off, monthly_weights
    )
    
    # Get monthly summary
    monthly_summary = calculation_service.get_monthly_summary(plan)
    
    # Get daily logs for progress tracking
    daily_logs = DailyLog.query.filter_by(user_id=current_user.id).all()
    daily_progress = {log.date: log.hours_billed for log in daily_logs}
    
    # Calculate monthly logged hours
    monthly_logged = {month: 0.0 for month in range(1, 13)}
    for log in daily_logs:
        monthly_logged[log.date.month] += log.hours_billed
    
    # Calculate progress metrics
    metrics = calculation_service.calculate_progress_metrics(
        goal.total_hours, plan, daily_progress
    )
    
    return render_template(
        'dashboard/index.html',
        goal=goal,
        monthly_summary=monthly_summary,
        monthly_logged=monthly_logged,
        metrics=metrics
    )

@bp.route('/calendar')
@login_required
def calendar():
    """Display the calendar view of billable hour targets."""
    # Get the month to display (default to current month)
    year = request.args.get('year', date.today().year, type=int)
    month = request.args.get('month', date.today().month, type=int)
    
    # Get the goal for this year
    goal = Goal.query.filter_by(user_id=current_user.id, year=year).first()
    
    if not goal:
        # Redirect if no goal exists
        return render_template('dashboard/no_goal.html', year=year)
    
    # Get days off
    days_off = [day.date for day in DayOff.query.filter_by(user_id=current_user.id)]
    
    # Get monthly weights
    monthly_weights_db = MonthlyWeight.query.filter_by(user_id=current_user.id, year=year).all()
    monthly_weights = {mw.month: mw.weight for mw in monthly_weights_db}
    
    # Calculate plan
    calculation_service = BillableHourCalculationService()
    plan = calculation_service.generate_plan(
        year, goal.total_hours, days_off, monthly_weights
    )
    
    # Get daily logs for actual hours
    daily_logs = DailyLog.query.filter_by(user_id=current_user.id).all()
    daily_logged = {log.date: log.hours_billed for log in daily_logs}
    
    # Generate calendar data
    import calendar
    cal = calendar.monthcalendar(year, month)
    
    # Prepare calendar weeks
    calendar_weeks = []
    for week in cal:
        week_data = []
        for day_num in week:
            if day_num == 0:
                # Day not in month
                week_data.append(None)
            else:
                current_date = date(year, month, day_num)
                day_data = {
                    'date': current_date,
                    'target_hours': plan.get(current_date, 0),
                    'logged_hours': daily_logged.get(current_date, 0),
                    'is_today': current_date == date.today()
                }
                week_data.append(day_data)
        calendar_weeks.append(week_data)
    
    return render_template(
        'dashboard/calendar.html',
        year=year,
        month=month,
        calendar_weeks=calendar_weeks
    )

@bp.route('/log_hours', methods=['GET', 'POST'])
@login_required
def log_hours():
    """Log actual billable hours for a day."""
    if request.method == 'POST':
        from datetime import datetime
        log_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        hours_billed = float(request.form['hours'])
        
        # Check if we already have a log for this date
        log = DailyLog.query.filter_by(user_id=current_user.id, date=log_date).first()
        
        if log:
            # Update existing log
            log.hours_billed = hours_billed
        else:
            # Create new log
            log = DailyLog(
                user_id=current_user.id,
                date=log_date,
                hours_billed=hours_billed
            )
            db.session.add(log)
        
        db.session.commit()
        return jsonify({'success': True})
    
    # For GET requests, return the form
    return render_template('dashboard/log_hours.html', today=date.today())