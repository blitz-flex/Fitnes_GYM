import os
from flask import render_template, request, redirect, url_for, current_app, abort
from werkzeug.utils import secure_filename
from .forms import ProgramRegistrationForm
from . import form_bp
from ...extensions import db
from ...models.user import UserAccount
from ...models.registration import ProgramRegistration
from flask_login import current_user, login_required


@form_bp.route("/program_registration", methods=['GET', 'POST'])
@login_required
def program_registration():
    # The logic of registering for a new program
    form = ProgramRegistrationForm()
    if form.validate_on_submit():
        registration = ProgramRegistration(
            user_id=current_user.id,
            full_name=current_user.name,
            program=form.program.data,
            phone_number=form.phone.data
        )
        db.session.add(registration)
        try:
            db.session.commit()
            return redirect(url_for('user.profile'))
        except Exception as e:
            db.session.rollback()
    return render_template('form/program_registration.html', form=form)


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
        return redirect(url_for('user.profile'))
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
