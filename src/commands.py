import click
import json
import os
from flask.cli import with_appcontext
from datetime import date
from flask import current_app
from .extensions import db
from .models.user import UserAccount
from .models.registration import ProgramRegistration
from .models.exercise import Exercise


@click.command('init-db')
@with_appcontext
def init_db_command():
    db.create_all()

    # 1. Create Admin User
    if not UserAccount.query.filter_by(username='admin').first():
        admin_user = UserAccount(
            first_name="Administrator",
            last_name="",
            email="admin@example.com",
            username="admin",
            birthdate=date(2000, 1, 1),
            gender="male"
        )
        admin_user.set_password("admin123")
        db.session.add(admin_user)

    # 2. Create 12 Sample Users
    names = [
        ("George", "Kakhidze", "male"), ("Nino", "Beridze", "female"),
        ("David", "Nozadze", "male"), ("Anna", "Maisuradze", "female"),
        ("Levan", "Sharikadze", "male"), ("Mariam", "Ghvinadze", "female"),
        ("Lasha", "Bekauri", "male"), ("Salome", "Pkhakadze", "female"),
        ("Irakli", "Kobakhidze", "male"), ("Tamari", "Lomidze", "female"),
        ("Zura", "Japaridze", "male"), ("Eka", "Beselia", "female")
    ]

    sample_users = []
    for i, (fname, lname, gender) in enumerate(names):
        username = f"user{i+1}"
        if not UserAccount.query.filter_by(username=username).first():
            user = UserAccount(
                first_name=fname,
                last_name=lname,
                email=f"{username}@example.com",
                username=username,
                gender=gender,
                birthdate=date(1990 + (i % 10), (i % 12) + 1, (i % 28) + 1),
                fitness_goal="Weight Loss" if i % 2 == 0 else "Muscle Gain",
                fitness_level="Intermediate" if i % 3 == 0 else "Beginner"
            )
            user.set_password("password123")
            db.session.add(user)
            sample_users.append(user)

    db.session.commit() # Save users to get IDs

    # 3. Create 12 Program Registrations
    programs = ["Yoga", "CrossFit", "Boxing", "Fitness", "Swimming", "Pilates", "Zumba"]
    times = ["08:00", "10:00", "14:00", "18:00", "20:00"]

    # Refresh users from DB
    all_users = UserAccount.query.filter(UserAccount.username != 'admin').all()

    for i in range(12):
        # Assign first 2 users to 2 programs each, others to 1
        user = all_users[i % len(all_users)]

        reg = ProgramRegistration(
            user_id=user.id,
            full_name=f"{user.first_name} {user.last_name}",
            phone_number=f"555-{100000 + i}",
            program=programs[i % len(programs)],
            preferred_time=times[i % len(times)],
            fitness_goal=user.fitness_goal
        )
        db.session.add(reg)

    db.session.commit()
    click.echo('✅ Database populated with Admin, 12 Users, and 12 Registrations!')


@click.command('init-exercises')
@with_appcontext
def init_exercises_command():
    """Populate database with exercises from JSON file"""
    json_path = os.path.join(current_app.root_path, 'static', 'data', 'exercises.json')
    
    if not os.path.exists(json_path):
        click.echo(f"❌ File not found: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        exercises_data = json.load(f)

    count = 0
    for item in exercises_data:
        # Check if exercise already exists
        existing = Exercise.query.get(item['id'])
        if not existing:
            exercise = Exercise(
                id=item['id'],
                name=item['name'],
                force=item.get('force'),
                level=item.get('level'),
                mechanic=item.get('mechanic'),
                equipment=item.get('equipment'),
                category=item.get('category')
            )
            exercise.primary_muscles = item.get('primaryMuscles', [])
            exercise.secondary_muscles = item.get('secondaryMuscles', [])
            exercise.instructions = item.get('instructions', [])
            exercise.images = item.get('images', [])
            
            db.session.add(exercise)
            count += 1
            
            if count % 100 == 0:
                db.session.commit()
                click.echo(f"Added {count} exercises...")

    db.session.commit()
    click.echo(f'✅ Exercise database populated successfully! Total added: {count} new exercises.')