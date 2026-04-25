from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, FileField, BooleanField, EmailField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError, Email
from flask_wtf.file import FileAllowed
import re

def validate_password_strength(form, field):
    """Custom validator for strong password requirements"""
    password = field.data
    if not password:
        return 

    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    if not re.search(r'[A-Z]', password):
        errors.append("Must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        errors.append("Must contain at least one lowercase letter")
    if not re.search(r'[0-9]', password):
        errors.append("Must contain at least one digit")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Must contain at least one special character (!@#$%^&*)")

    if errors:
        raise ValidationError(' | '.join(errors))

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(message="First name is required.")])
    last_name = StringField('Last Name', validators=[DataRequired(message="Last name is required.")])
    email = EmailField('Email Address', validators=[
        DataRequired(message="Email is required."),
        Email(message="Invalid email address.")
    ])
    username = StringField('Username', validators=[
        DataRequired(message="Username is required."),
        Length(min=3, max=20, message="Username must be between 3 and 20 characters.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required."),
        validate_password_strength
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password."),
        EqualTo('password', message='Passwords must match.')
    ])
    birthdate = DateField('Birthdate', format='%Y-%m-%d', validators=[DataRequired(message="Birthdate is required.")])
    gender = SelectField('Gender', choices=[
        ('', 'Select Gender'), 
        ('male', 'Male'), 
        ('female', 'Female'), 
        ('other', 'Other')
    ], validators=[DataRequired(message="Please select your gender.")])
    profile_image = FileField('Profile Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Only images are allowed!')
    ])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Please enter your username"),
        Length(min=3, max=20, message="Username must be 3-20 characters")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Please enter your password"),
        Length(min=4, message="Password must be at least 4 characters")
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RequestResetForm(FlaskForm):
    email = EmailField('Email Address', validators=[
        DataRequired(message="Email is required."),
        Email(message="Invalid email address.")
    ])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(message="Password is required."),
        validate_password_strength
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message="Please confirm your password."),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Reset Password')