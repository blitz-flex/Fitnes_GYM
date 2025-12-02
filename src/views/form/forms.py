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
        raise ValidationError('არასწორი ტელეფონის ნომერი. გამოიყენეთ ქართული ფორმატი (მაგ: 5XX XXX XXX)')

class ProgramRegistrationForm(FlaskForm):
    phone = StringField('ტელეფონის ნომერი', validators=[DataRequired(), validate_georgian_phone])
    program = SelectField('პროგრამა',
                         choices=[
                             ('ძალისხმევა', 'ძალისხმევა'),
                             ('კარდიო', 'კარდიო'),
                             ('ფიტნესი', 'ფიტნესი'),
                             ('იოგა', 'იოგა'),
                             ('პილატესი', 'პილატესი'),
                             ('ცურვა', 'ცურვა'),
                             ('ბოქსი', 'ბოქსი'),
                             ('კროსფიტი', 'კროსფიტი')
                         ],
                         validators=[DataRequired()])
    submit = SubmitField('რეგისტრაცია')
