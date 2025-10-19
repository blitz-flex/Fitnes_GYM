from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, SubmitField, DateField, RadioField, FileField
from wtforms.validators import DataRequired, EqualTo, Regexp
from flask_wtf.file import FileAllowed

class ProgramRegistrationForm(FlaskForm):
    name = StringField('სახელი და გვარი', validators=[DataRequired(message="გთხოვთ შეიყვანოთ სახელი და გვარი.")])
    program = SelectField('აირჩიეთ პროგრამა',
                          choices=[
                              ('', 'აირჩიეთ პროგრამა'), ('yoga', 'იოგა'), ('crossfit', 'კროსფიტი'),
                              ('gym', 'ძალოსნობა'), ('boxing', 'კრივი'), ('pilates', 'პილატესი'), ('swimming', 'ცურვა')
                          ],
                          validators=[DataRequired(message="გთხოვთ აირჩიოთ პროგრამა.")])
    phone = StringField('ტელეფონის ნომერი', validators=[DataRequired(), Regexp(r'^[5][0-9]{8}$', message="ნომერი უნდა იყოს 9 ციფრიანი და იწყებოდეს 5-ით.")])
    submit = SubmitField('დაიწყე ვარჯიში')

class SimpleAccountForm(FlaskForm):
    name = StringField('სახელი და გვარი', validators=[DataRequired(message="გთხოვთ შეიყვანოთ სახელი და გვარი.")])
    username = StringField('მომხმარებლის სახელი', validators=[DataRequired(message="გთხოვთ შეიყვანოთ მომხმარებლის სახელი.")])
    password = PasswordField('პაროლი', validators=[DataRequired(message="გთხოვთ შეიყვანოთ პაროლი.")])
    confirm_password = PasswordField('გაიმეორეთ პაროლი', validators=[DataRequired(), EqualTo('password', message='პაროლები არ ემთხვევა.')])
    birthdate = DateField('დაბადების თარიღი', format='%Y-%m-%d', validators=[DataRequired(message="გთხოვთ შეიყვანოთ დაბადების თარიღი.")])
    gender = SelectField('სქესი', 
                          choices=[('', 'აირჩიეთ სქესი'), ('male', 'მამაკაცი'), ('female', 'ქალი'), ('other', 'სხვა')],
                          validators=[DataRequired(message="გთხოვთ აირჩიოთ სქესი.")])
    profile_image = FileField('პროფილის სურათი', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'დაშვებულია მხოლოდ სურათები!')])
    submit = SubmitField('რეგისტრაცია')