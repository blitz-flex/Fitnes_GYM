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
    db.drop_all()
    db.create_all()

    # Create Admin User
    admin_user = UserAccount(
        name="Administrator",
        username="admin",
        birthdate=date(2000, 1, 1),
        gender="male"
    )
    admin_user.set_password("admin123")
    db.session.add(admin_user)

    db.session.commit()
    click.echo('✅ Database initialization complete! Created "admin" account.')


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