import click
from flask.cli import with_appcontext
from datetime import date
from .extensions import db
from .models.user import UserAccount
from .models.registration import ProgramRegistration

@click.command('init-db')
@with_appcontext
def init_db_command():
    # Clear existing data and create new tables with test data
    db.drop_all()
    db.create_all()

    registrations_data = [{"name": "ნანა ნაცვლიშვილი", "program": "პილატესი", "phone": "555667788"}]
    users_data = [{"name": "ლუკა ლუკაშვილი", "username": "luka.strong", "password": "password456", "birthdate": date(1995, 8, 15), "gender": "male"}]

    for data in registrations_data:
        db.session.add(ProgramRegistration(**data))
    for data in users_data:
        db.session.add(UserAccount(**data))

    db.session.commit()
    click.echo('✅ ბაზის ინიციალიზაცია დასრულდა!')