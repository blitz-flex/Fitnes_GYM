from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, FileField, BooleanField
from wtforms.validators import DataRequired, EqualTo
from flask_wtf.file import FileAllowed

class RegistrationForm(FlaskForm):
    name = StringField('სახელი და გვარი', validators=[DataRequired(message="გთხოვთ შეიყვანოთ სახელი და გვარი.")])
    username = StringField('მომხმარებლის სახელი', validators=[DataRequired(message="გთხოვთ შეიყვანოთ მომხმარებლის სახელი.")])
    password = PasswordField('პაროლი', validators=[DataRequired(message="გთხოვთ შეიყვანოთ პაროლი.")])
    confirm_password = PasswordField('გაიმეორეთ პაროლი', validators=[DataRequired(), EqualTo('password', message='პაროლები არ ემთხვევა.')])
    birthdate = DateField('დაბადების თარიღი', format='%Y-%m-%d', validators=[DataRequired(message="გთხოვთ შეიყვანოთ დაბადების თარიღი.")])
    gender = SelectField('სქესი', choices=[('', 'აირჩიეთ სქესი'), ('male', 'მამაკაცი'), ('female', 'ქალი'), ('other', 'სხვა')], validators=[DataRequired(message="გთხოვთ აირჩიოთ სქესი.")])
    profile_image = FileField('პროფილის სურათი', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'დაშვებულია მხოლოდ სურათები!')])
    submit = SubmitField('რეგისტრაცია')

class LoginForm(FlaskForm):
    username = StringField('მომხმარებლის სახელი', validators=[DataRequired("შეიყვანეთ მომხმარებლის სახელი.")])
    password = PasswordField('პაროლი', validators=[DataRequired("შეიყვანეთ პაროლი.")])
    remember = BooleanField('დამიმახსოვრე')
    submit = SubmitField('შესვლა')