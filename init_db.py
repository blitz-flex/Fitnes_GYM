from app import app, db, ProgramRegistration, UserAccount
from datetime import date

# Test Case Data
registrations_data = [
    {
        "name": "ნანა ნაცვლიშვილი",
        "program": "პილატესი",
        "phone": "555667788"
    }
]

users_data = [
    {
        "name": "ლუკა ლუკაშვილი",
        "username": "luka.strong",
        "password": "password456",
        "birthdate": date(1995, 8, 15),
        "gender": "male",
        "profile_image": None
    }
]

with app.app_context():
    db.create_all()


    for data in registrations_data:

        existing = ProgramRegistration.query.filter_by(
            name=data['name'],
            program=data['program']
        ).first()

        if not existing:
            registration = ProgramRegistration(**data)
            db.session.add(registration)

    for data in users_data:

        existing = UserAccount.query.filter_by(username=data['username']).first()

        if not existing:
            user = UserAccount(**data)
            db.session.add(user)


    db.session.commit()
    print("✅ Initialization complete!!")