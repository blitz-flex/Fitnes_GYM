from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, SubmitField, DateField, RadioField, FileField
from wtforms.validators import DataRequired, EqualTo, Regexp, ValidationError
from flask_wtf.file import FileAllowed

class ProgramRegistrationForm(FlaskForm):
    name = StringField('სახელი და გვარი', validators=[DataRequired(message="გთხოვთ შეიყვანოთ სახელი და გვარი.")])
    program = SelectField('აირჩიეთ პროგრამა',
                          choices=[
                              ('', 'აირჩიეთ პროგრამა'),
                              ('yoga', 'იოგა (₾80/თვე)'),
                              ('crossfit', 'კროსფიტი (₾100/თვე)'),
                              ('gym', 'ძალოსნობა (₾120/თვე)'),
                              ('boxing', 'კრივი (₾90/თვე)'),
                              ('pilates', 'პილატესი (₾85/თვე)'),
                              ('swimming', 'ცურვა (₾150/თვე)')
                          ],
                          validators=[DataRequired(message="გთხოვთ აირჩიოთ პროგრამა.")])
    phone = StringField('ტელეფონის ნომერი',
                        validators=[
                            DataRequired(message="გთხოვთ შეიყვანოთ ტელეფონის ნომერი."),
                            Regexp(r'^[5][0-9]{8}$',
                                   message="შეიყვანეთ +995 5XXXXXXXXX ფორმატში.")
                        ])
    submit = SubmitField('დაიწყე ვარჯიში')

    # Additional validation
    def validate_program(self, field):
        if field.data == "":
            raise ValidationError("გთხოვთ აირჩიოთ პროგრამა.")

class SimpleAccountForm(FlaskForm):
    name = StringField('სახელი და გვარი', validators=[DataRequired(message="გთხოვთ შეიყვანოთ სახელი და გვარი.")])
    username = StringField('მომხმარებლის სახელი', validators=[DataRequired(message="გთხოვთ შეიყვანოთ მომხმარებლის სახელი.")])
    password = PasswordField('პაროლი', validators=[DataRequired(message="გთხოვთ შეიყვანოთ პაროლი.")])
    confirm_password = PasswordField('გაიმეორეთ პაროლი',
                                     validators=[DataRequired(message="გთხოვთ გაიმეოროთ პაროლი."),
                                                 # Check that the field matches the 'password' field
                                                 EqualTo('password', message='პაროლები არ ემთხვევა')])
    birthdate = DateField('დაბადების თარიღი', format='%Y-%m-%d', validators=[DataRequired(message="გთხოვთ შეიყვანოთ დაბადების თარიღი.")])
    gender = RadioField('სქესი',
                        choices=[('male', 'მამაკაცი'), ('female', 'ქალი')],
                        validators=[DataRequired(message="გთხოვთ აირჩიოთ სქესი.")])
    profile_image = FileField('პროფილის სურათი',
                              validators=[DataRequired(message="გთხოვთ ატვირთოთ სურათი."),
                                          # File type restriction
                                          FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Only images are allowed.(jpg, png, jpeg, gif)!')])
    submit = SubmitField('რეგისტრაცია')