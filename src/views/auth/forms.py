from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, FileField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from flask_wtf.file import FileAllowed
import re

def validate_password_strength(form, field):
    """Custom validator for strong password requirements"""
    password = field.data
    if not password:
        return  # DataRequired will handle empty passwords

    errors = []

    if len(password) < 8:
        errors.append("პაროლი მინიმუმ 8 სიმბოლო უნდა იყოს")

    if not re.search(r'[A-Z]', password):
        errors.append("უნდა შეიცავდეს მინიმუმ ერთ დიდ ასოს")

    if not re.search(r'[a-z]', password):
        errors.append("უნდა შეიცავდეს მინიმუმ ერთ პატარა ასოს")

    if not re.search(r'[0-9]', password):
        errors.append("უნდა შეიცავდეს მინიმუმ ერთ ციფრს")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("უნდა შეიცავდეს მინიმუმ ერთ სპეციალურ სიმბოლოს (!@#$%^&*)")

    if errors:
        raise ValidationError(' | '.join(errors))

class RegistrationForm(FlaskForm):
    name = StringField('სახელი და გვარი', validators=[DataRequired(message="ეს ველი აუცილებელია.")])
    username = StringField('მომხმარებლის სახელი', validators=[DataRequired(message="ეს ველი აუცილებელია.")])
    password = PasswordField('პაროლი', validators=[
        DataRequired(message="ეს ველი აუცილებელია."),
        validate_password_strength
    ])
    confirm_password = PasswordField('გაიმეორეთ პაროლი', validators=[
        DataRequired(message="ეს ველი აუცილებელია."),
        EqualTo('password', message='პაროლები არ ემთხვევა.')
    ])
    birthdate = DateField('დაბადების თარიღი', format='%Y-%m-%d', validators=[DataRequired(message="ეს ველი აუცილებელია.")])
    gender = SelectField('სქესი', choices=[('', 'აირჩიეთ სქესი'), ('male', 'მამაკაცი'), ('female', 'ქალი'), ('other', 'სხვა')], validators=[DataRequired(message="ეს ველი აუცილებელია.")])
    profile_image = FileField('პროფილის სურათი', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'დაშვებულია მხოლოდ სურათები!')])
    submit = SubmitField('რეგისტრაცია')

class LoginForm(FlaskForm):
    username = StringField('მომხმარებლის სახელი', validators=[
        DataRequired(message="შეიყვანეთ მომხმარებლის სახელი"),
        Length(min=3, max=20, message="მომხმარებლის სახელი უნდა იყოს 3-20 სიმბოლო")
    ])
    password = PasswordField('პაროლი', validators=[
        DataRequired(message="შეიყვანეთ პაროლი"),
        Length(min=4, message="პაროლი მინიმუმ 4 სიმბოლო ")
    ])
    remember = BooleanField('დამიმახსოვრე')
    submit = SubmitField('შესვლა')