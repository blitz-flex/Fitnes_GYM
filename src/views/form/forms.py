from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class ProgramRegistrationForm(FlaskForm):
    name = StringField('სრული სახელი', validators=[DataRequired(), Length(min=4, max=100)])
    program = SelectField('პროგრამა', choices=[
        ('', 'აირჩიეთ პროგრამა'),  # საწყისი ველი
        ('yoga', 'იოგა'),
        ('crosfit', 'კროსფიტი'),
        ('athletics', 'ძალოსნობა'),
        ('boxing', 'კრივი'),
        ('pilates', 'პილატესი'),
        ('swimming', 'ცურვა')
    ], validators=[DataRequired()])
    phone = StringField('ტელეფონის ნომერი', validators=[DataRequired()])
    # <<< ცვლილება: ღილაკის ტექსტი შეიცვალა 'გაგზავნით'
    submit = SubmitField('გაგზავნა')