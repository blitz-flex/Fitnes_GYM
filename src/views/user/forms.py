from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField, PasswordField, IntegerField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, EqualTo, Optional
from flask_babel import lazy_gettext as _

class ProfileUpdateForm(FlaskForm):
    name = StringField(_('Full Name'), validators=[DataRequired(), Length(min=2, max=100)])
    birthdate = DateField(_('Birth Date'), validators=[DataRequired()])
    gender = SelectField(_('Gender'), 
                        choices=[('male', _('Male')), ('female', _('Female'))],
                        validators=[DataRequired()])
    profile_image = FileField(_('Profile Picture'), 
                             validators=[FileAllowed(['jpg', 'png', 'jpeg'], _('Images only!'))])
    submit = SubmitField(_('Update'))

class SettingsForm(FlaskForm):
    weight = StringField(_('Weight (kg)'), validators=[Optional()])
    height = StringField(_('Height (cm)'), validators=[Optional()])
    target_weight = StringField(_('Target Weight (kg)'), validators=[Optional()])
    age = IntegerField(_('Age'), validators=[Optional()])
    gender = SelectField(_('Gender'), choices=[('Male', _('Male')), ('Female', _('Female')), ('Other', _('Other'))])
    fitness_goal = SelectField(_('Fitness Goal'), 
                               choices=[('', _('Select Goal')), 
                                        ('Weight Loss', _('Weight Loss')), 
                                        ('Muscle Gain', _('Muscle Gain')), 
                                        ('Endurance', _('Endurance')), 
                                        ('Maintenance', _('Maintenance'))])
    activity_level = SelectField(_('Activity Level'), 
                                 choices=[('', _('Select Activity Level')), 
                                          ('Sedentary', _('Sedentary')), 
                                          ('Lightly Active', _('Lightly Active')), 
                                          ('Moderately Active', _('Moderately Active')), 
                                          ('Very Active', _('Very Active'))])
    fitness_level = SelectField(_('Fitness Level'), choices=[('Beginner', _('Beginner')), ('Intermediate', _('Intermediate')), ('Advanced', _('Advanced'))])
    workout_frequency = IntegerField(_('Workout Frequency (days/week)'), validators=[Optional()])
    
    # Advanced Settings
    weekly_digest = SelectField(_('Weekly Progress Digest'), choices=[('1', _('Enabled')), ('0', _('Disabled'))])
    ai_coach_personality = SelectField(_('AI Coach Personality'), choices=[('supportive', _('Supportive & Friendly')), ('drill_sergeant', _('Drill Sergeant (Strict)')), ('scientific', _('Scientific & Data-Driven'))])
    sore_muscles = StringField(_('Sore Muscles'), validators=[Optional()])
    
    email_notifications = SelectField(_('Email Notifications'), choices=[('1', _('Enabled')), ('0', _('Disabled'))])
    dark_mode = SelectField(_('Theme Preference'), choices=[('1', _('Dark Mode')), ('0', _('Light Mode'))])
    language = SelectField(_('Language'), choices=[('en', _('English')), ('ka', _('Georgian'))])
    submit = SubmitField(_('Save Settings'))

class SecurityForm(FlaskForm):
    email = StringField(_('Email Address'), validators=[DataRequired(), Length(max=120)])
    current_password = PasswordField(_('Current Password'))
    new_password = PasswordField(_('New Password'), validators=[
        Length(min=8, message=_("Password must be at least 8 characters long"))
    ])
    confirm_password = PasswordField(_('Confirm New Password'), validators=[
        DataRequired(),
        EqualTo('new_password', message=_('Passwords must match.'))
    ])
    submit_security = SubmitField(_('Update Password'))

class DeleteAccountForm(FlaskForm):
    password = PasswordField(_('Enter Password to Confirm Deletion'), validators=[DataRequired()])
    submit_delete = SubmitField(_('Permanently Delete Account'))
