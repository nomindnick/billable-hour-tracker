# app/setup/routes.py
from datetime import date
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import current_user, login_required
from app import db
from app.setup import bp
from app.setup.forms import GoalForm, DaysOffForm, MonthlyWeightForm, DayOffForm
from app.models import Goal, DayOff, MonthlyWeight

@bp.route('/wizard', methods=['GET', 'POST'])
@login_required
def wizard():
    # Check if user already has goals set up
    if current_user.goals.first() and 'setup_step' not in session:
        flash('You have already completed the setup process.')
        return redirect(url_for('main.index'))
    
    # Get current step from session or set to 1
    step = session.get('setup_step', 1)
    
    if step == 1:
        # Goal setup
        form = GoalForm()
        if form.validate_on_submit():
            # Store data in session
            session['setup_year'] = form.year.data
            session['setup_total_hours'] = form.total_hours.data
            session['setup_step'] = 2  # Move to next step
            return redirect(url_for('setup.wizard'))
        
        return render_template('setup/goal.html', title='Setup Goal', form=form)
    
    elif step == 2:
        # Days off setup
        form = DaysOffForm()
        
        # Handle form submission
        if form.validate_on_submit():
            # If "Add Another Day" button was clicked
            if 'add_day' in request.form:
                form.days_off.append_entry()
                return render_template('setup/days_off.html', title='Setup Days Off', form=form)
            
            # If "Next" button was clicked, store data in session
            days_off_data = []
            for day_off_form in form.days_off:
                day_off = {
                    'date': day_off_form.date.data.strftime('%Y-%m-%d'),
                    'type': day_off_form.type.data
                }
                days_off_data.append(day_off)
            
            session['setup_days_off'] = days_off_data
            session['setup_step'] = 3  # Move to next step
            return redirect(url_for('setup.wizard'))
        
        return render_template('setup/days_off.html', title='Setup Days Off', form=form)
    
    elif step == 3:
        # Monthly weights setup
        form = MonthlyWeightForm()
        if form.validate_on_submit():
            # Process all form data and save to database
            
            # Save Goal
            year = session.get('setup_year')
            total_hours = session.get('setup_total_hours')
            
            goal = Goal(user_id=current_user.id, year=year, total_hours=total_hours)
            db.session.add(goal)
            
            # Save Days Off
            days_off_data = session.get('setup_days_off', [])
            for day_off_data in days_off_data:
                day_off = DayOff(
                    user_id=current_user.id,
                    date=date.fromisoformat(day_off_data['date']),
                    type=day_off_data['type']
                )
                db.session.add(day_off)
            
            # Save Monthly Weights
            months = [
                form.january.data, form.february.data, form.march.data, 
                form.april.data, form.may.data, form.june.data,
                form.july.data, form.august.data, form.september.data,
                form.october.data, form.november.data, form.december.data
            ]
            
            for i, weight in enumerate(months, 1):
                monthly_weight = MonthlyWeight(
                    user_id=current_user.id,
                    year=year,
                    month=i,
                    weight=weight
                )
                db.session.add(monthly_weight)
            
            # Commit all changes
            db.session.commit()
            
            # Clear setup session data
            session.pop('setup_step', None)
            session.pop('setup_year', None)
            session.pop('setup_total_hours', None)
            session.pop('setup_days_off', None)
            
            flash('Setup completed successfully!')
            return redirect(url_for('main.index'))
        
        return render_template('setup/monthly_weights.html', title='Setup Monthly Weights', form=form)
    
    # If something goes wrong, redirect to first step
    session['setup_step'] = 1
    return redirect(url_for('setup.wizard'))