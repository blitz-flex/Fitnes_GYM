from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
import re

def validate_georgian_phone(form, field):
    """Custom validator for Georgian phone numbers"""
    phone = field.data
    if not phone:
        return  # DataRequired will handle empty phones

    # Remove all spaces, dashes, and plus signs for validation
    clean_phone = re.sub(r'[\s\-+()]', '', phone)

    # Georgian phone number patterns
    patterns = [
        r'^5\d{8}$',        # 5xxxxxxxx (9 digits starting with 5)
        r'^995\d{9}$',      # 995xxxxxxxxx (country code + number)
        r'^9955\d{8}$',     # 9955xxxxxxxx (alternative format)
        r'^032\d{6}$',      # 032xxxxxx (Tbilisi landline)
        r'^0\d{8}$'         # 0xxxxxxxx (other landlines)
    ]

    if not any(re.match(pattern, clean_phone) for pattern in patterns):
        raise ValidationError('Invalid phone number. Please use Georgian format (e.g., 5XX XXX XXX)')

class ProgramRegistrationForm(FlaskForm):
    phone = StringField('Phone Number', validators=[
        DataRequired(message="Phone number is required."), 
        validate_georgian_phone
    ])
    program = SelectField('Select Program',
                         choices=[
                             ('Strength Training', 'Strength Training'),
                             ('Cardio', 'Cardio'),
                             ('Fitness', 'Fitness'),
                             ('Yoga', 'Yoga'),
                             ('Pilates', 'Pilates'),
                             ('Swimming', 'Swimming'),
                             ('Boxing', 'Boxing'),
                             ('Crossfit', 'Crossfit')
                         ],
                         validators=[DataRequired(message="Please select a program.")])
    preferred_time = SelectField('Preferred Time',
                               choices=[
                                   ('Morning (08:00 - 12:00)', 'Morning (08:00 - 12:00)'),
                                   ('Afternoon (12:00 - 17:00)', 'Afternoon (12:00 - 17:00)'),
                                   ('Evening (17:00 - 22:00)', 'Evening (17:00 - 22:00)')
                               ],
                               validators=[DataRequired(message="Please select a preferred time.")])
    start_date = StringField('When would you like to start?', render_kw={"placeholder": "e.g. From tomorrow, May 1st"}, validators=[DataRequired(message="Start date is required.")])
    fitness_goal = SelectField('Your Fitness Goal',
                             choices=[
                                 ('Weight Loss', 'Weight Loss'),
                                 ('Muscle Gain', 'Muscle Gain'),
                                 ('Body Toning', 'Body Toning'),
                                 ('Endurance', 'Endurance'),
                                 ('Health Improvement', 'Health Improvement')
                             ],
                             validators=[DataRequired(message="Please select a goal.")])
    experience_level = SelectField('Experience Level',
                                 choices=[
                                     ('Beginner', 'Beginner'),
                                     ('Intermediate', 'Intermediate'),
                                     ('Professional', 'Professional')
                                 ],
                                 validators=[DataRequired(message="Please select your experience level.")])
    submit = SubmitField('Register Now')

class FreeSessionForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(message="Name is required.")])
    phone = StringField('Phone Number', validators=[
        DataRequired(message="Phone number is required."), 
        validate_georgian_phone
    ])
    preferred_date = StringField('Preferred Date', render_kw={"type": "date"}, validators=[DataRequired(message="Date is required.")])
    preferred_time = SelectField('Preferred Time',
                               choices=[
                                   ('Morning (08:00 - 12:00)', 'Morning (08:00 - 12:00)'),
                                   ('Afternoon (12:00 - 17:00)', 'Afternoon (12:00 - 17:00)'),
                                   ('Evening (17:00 - 22:00)', 'Evening (17:00 - 22:00)')
                               ],
                               validators=[DataRequired(message="Please select a preferred time.")])
    fitness_goal = SelectField('Primary Goal',
                             choices=[
                                 ('Weight Loss', 'Weight Loss'),
                                 ('Muscle Gain', 'Muscle Gain'),
                                 ('General Fitness', 'General Fitness'),
                                 ('Consultation', 'Just want to look around')
                             ],
                             validators=[DataRequired(message="Please select a goal.")])
    submit = SubmitField('Book Free Session')
