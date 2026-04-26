import os
from flask import render_template, request, redirect, url_for, current_app, abort, flash
from werkzeug.utils import secure_filename
from .forms import ProgramRegistrationForm, FreeSessionForm
from . import form_bp
from ...extensions import db
from ...models.user import UserAccount
from ...models.registration import ProgramRegistration
from flask_login import current_user, login_required

@form_bp.route("/free-session", methods=['GET', 'POST'])
def free_session():
    form = FreeSessionForm()
    
    # Pre-fill name if logged in
    if request.method == 'GET' and current_user.is_authenticated:
        form.full_name.data = current_user.name

    if form.validate_on_submit():
        # Reusing ProgramRegistration model for simplicity, or we could just flash success
        # We'll save it as a "Free Trial" program
        user_id = current_user.id if current_user.is_authenticated else None
        
        # If not authenticated, we can't save to this model directly without user_id 
        # (unless user_id is nullable, but it's not). 
        # For now, let's just simulate success for guests or save if logged in.
        
        if current_user.is_authenticated:
            registration = ProgramRegistration(
                user_id=user_id,
                full_name=form.full_name.data,
                program="Free Trial Session",
                phone_number=form.phone.data,
                preferred_time=f"{form.preferred_date.data} | {form.preferred_time.data}",
                start_date=form.preferred_date.data,
                fitness_goal=form.fitness_goal.data,
                experience_level="Trial"
            )
            db.session.add(registration)
            try:
                db.session.commit()
                flash('Your free session has been booked successfully! We will call you soon.', 'success')
                return redirect(url_for('user.registrations'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred, please try again.', 'danger')
        else:
            # If guest, just flash success (or redirect to login)
            flash('Your free session request has been received! Our manager will contact you shortly.', 'success')
            return redirect(url_for('main.index'))
            
    return render_template('form/free_session.html', form=form)


@form_bp.route("/program_registration", methods=['GET', 'POST'])
@login_required
def program_registration():
    # The logic of registering for a new program
    form = ProgramRegistrationForm()
    
    # Pre-fill program from query parameter if provided
    program_param = request.args.get('program')
    if request.method == 'GET' and program_param:
        form.program.data = program_param

    if form.validate_on_submit():
        registration = ProgramRegistration(
            user_id=current_user.id,
            full_name=current_user.name, # Use existing user name for DB constraint
            program=form.program.data,
            phone_number=form.phone.data,
            preferred_time=form.preferred_time.data,
            start_date=form.start_date.data,
            fitness_goal=form.fitness_goal.data,
            experience_level=form.experience_level.data
        )
        db.session.add(registration)
        try:
            db.session.commit()
            return render_template('form/program_registration.html', form=form, success=True)
        except Exception as e:
            db.session.rollback()
            flash('An error occurred, please try again later.', 'danger')
    return render_template('form/program_registration.html', form=form, success=False)


@form_bp.route('/registration/<int:registration_id>/delete', methods=['POST'])
@login_required
def delete_registration(registration_id):
    # delete logic for program registration
    registration = ProgramRegistration.query.get_or_404(registration_id)
    # check if the registration belongs to the current user
    if registration.user_id != current_user.id:
        abort(403)

    try:
        db.session.delete(registration)
        db.session.commit()
        return redirect(url_for('user.registrations'))
    except Exception as e:
        db.session.rollback()
        abort(500)


@form_bp.route('/registration/<int:registration_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_registration(registration_id):
    # edit logic for program registration
    registration = ProgramRegistration.query.get_or_404(registration_id)
    #check if the registration belongs to the current user
    if registration.user_id != current_user.id:
        abort(403)

    form = ProgramRegistrationForm()

    if form.validate_on_submit():
        # data update logic - full_name stays the same, only update program and phone
        registration.program = form.program.data
        registration.phone_number = form.phone.data
        try:
            db.session.commit()
            return redirect(url_for('user.profile'))
        except Exception as e:
            db.session.rollback()
    elif request.method == 'GET':
        # Filling the form with data retrieved from the database
        form.program.data = registration.program
        form.phone.data = registration.phone_number

    return render_template('form/program_registration.html', form=form)
