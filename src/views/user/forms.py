from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField, PasswordField, IntegerField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, EqualTo, Optional

class ProfileUpdateForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    birthdate = DateField('Birth Date', validators=[DataRequired()])
    gender = SelectField('Gender', 
                        choices=[('male', 'Male'), ('female', 'Female')],
                        validators=[DataRequired()])
    profile_image = FileField('Profile Picture', 
                             validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Update')

class SettingsForm(FlaskForm):
    weight = StringField('Weight (kg)', validators=[Optional()])
    height = StringField('Height (cm)', validators=[Optional()])
    target_weight = StringField('Target Weight (kg)', validators=[Optional()])
    age = IntegerField('Age', validators=[Optional()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    fitness_goal = SelectField('Fitness Goal', 
                               choices=[('', 'Select Goal'), 
                                        ('Weight Loss', 'Weight Loss'), 
                                        ('Muscle Gain', 'Muscle Gain'), 
                                        ('Endurance', 'Endurance'), 
                                        ('Maintenance', 'Maintenance')])
    activity_level = SelectField('Activity Level', 
                                 choices=[('', 'Select Activity Level'), 
                                          ('Sedentary', 'Sedentary'), 
                                          ('Lightly Active', 'Lightly Active'), 
                                          ('Moderately Active', 'Moderately Active'), 
                                          ('Very Active', 'Very Active')])
    fitness_level = SelectField('Fitness Level', choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')])
    workout_frequency = IntegerField('Workout Frequency (days/week)', validators=[Optional()])
    
    # Advanced Settings
    weekly_digest = SelectField('Weekly Progress Digest', choices=[('1', 'Enabled'), ('0', 'Disabled')])
    ai_coach_personality = SelectField('AI Coach Personality', choices=[('supportive', 'Supportive & Friendly'), ('drill_sergeant', 'Drill Sergeant (Strict)'), ('scientific', 'Scientific & Data-Driven')])
    sore_muscles = StringField('Sore Muscles', validators=[Optional()])
    
    email_notifications = SelectField('Email Notifications', choices=[('1', 'Enabled'), ('0', 'Disabled')])
    dark_mode = SelectField('Theme Preference', choices=[('1', 'Dark Mode'), ('0', 'Light Mode')])
    language = SelectField('Language', choices=[('en', 'English'), ('ka', 'Georgian')])
    submit = SubmitField('Save Settings')

class SecurityForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Length(max=120)])
    current_password = PasswordField('Current Password')
    new_password = PasswordField('New Password', validators=[
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match.')
    ])
    submit_security = SubmitField('Update Password')

class DeleteAccountForm(FlaskForm):
    password = PasswordField('Enter Password to Confirm Deletion', validators=[DataRequired()])
    submit_delete = SubmitField('Permanently Delete Account')
