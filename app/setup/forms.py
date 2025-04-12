# app/setup/forms.py
from datetime import date
from flask_wtf import FlaskForm
from wtforms import IntegerField, DateField, SelectField, FloatField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, NumberRange, Optional

class GoalForm(FlaskForm):
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=2000, max=2100)], 
                        default=date.today().year)
    total_hours = IntegerField('Annual Billable Hour Goal', 
                               validators=[DataRequired(), NumberRange(min=0, max=4000)])
    submit = SubmitField('Next')

class DayOffForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    type = SelectField('Type', choices=[
        ('Holiday', 'Firm Holiday'),
        ('Vacation', 'Vacation'),
        ('Personal', 'Personal Day')
    ])

class DaysOffForm(FlaskForm):
    days_off = FieldList(FormField(DayOffForm), min_entries=1)
    submit = SubmitField('Next')
    add_day = SubmitField('Add Another Day')

class MonthlyWeightForm(FlaskForm):
    january = FloatField('January', validators=[DataRequired(), NumberRange(min=0.1, max=2.0)], default=1.0)
    february = FloatField('February', validators=[DataRequired(), NumberRange(min=0.1, max=2.0)], default=1.0)
    march = FloatField('March', validators=[DataRequired(), NumberRange(min=0.1, max=2.0)], default=1.0)
    april = FloatField('April', validators=[DataRequired(), NumberRange(min=0.1, max=2.0)], default=1.0)
    may = FloatField('May', validators=[DataRequired(), NumberRange(min=0.1, max=2.0)], default=1.0)
    june = FloatField('June', validators=[DataRequired(), NumberRange(min=0.1, max=2.0)], default=1.0)
    july = FloatField('July', validators=[DataRequired(), NumberRange(min=0.1, max=2.0)], default=1.0)
    august = FloatField('August', validators=[DataRequired(), NumberRange(min=0.1, max=2.0)], default=1.0)
    september = FloatField('September', validators=[DataRequired(), NumberRange(min=0.1, max=2.0)], default=1.0)
    october = FloatField('October', validators=[DataRequired(), NumberRange(min=0.1, max=2.0)], default=1.0)
    november = FloatField('November', validators=[DataRequired(), NumberRange(min=0.1, max=2.0)], default=1.0)
    december = FloatField('December', validators=[DataRequired(), NumberRange(min=0.1, max=2.0)], default=1.0)
    
    submit = SubmitField('Finish Setup')