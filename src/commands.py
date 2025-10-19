import click
from flask.cli import with_appcontext
from datetime import date
from .extensions import db
from .models.user import UserAccount
from .models.registration import ProgramRegistration


@click.command('init-db')
@with_appcontext
def init_db_command():
    db.drop_all()
    db.create_all()

    test_user = UserAccount(
        name="ლუკა ლუკაშვილი",
        username="luka.strong",
        birthdate=date(1995, 8, 15),
        gender="male"
    )
    test_user.set_password("password456")
    db.session.add(test_user)

    db.session.commit()

    registration = ProgramRegistration(
        user_id=test_user.id,
        full_name="ლუკა ლუკაშვილი",
        program="pilates",
        phone_number="555667788"
    )
    db.session.add(registration)

    db.session.commit()
    click.echo('✅ ბაზის ინიციალიზაცია დასრულდა! შეიქმნა ტესტ-მომხმარებელი "luka.strong".')