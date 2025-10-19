# /src/views/form/routes.py
import os
from flask import render_template, request, redirect, url_for, flash, current_app, abort
from werkzeug.utils import secure_filename
from .forms import ProgramRegistrationForm
from . import form_bp
from ...utils import flash_errors
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
            full_name=form.name.data,
            program=form.program.data,
            phone_number=form.phone.data
        )
        db.session.add(registration)
        try:
            db.session.commit()
            flash('პროგრამაზე რეგისტრაცია წარმატებით დასრულდა!', 'success')
            return redirect(url_for('user.profile'))
        except Exception as e:
            db.session.rollback()
            flash('დაფიქსირდა შეცდომა. გთხოვთ სცადოთ თავიდან.', 'danger')
    else:
        flash_errors(form)
    return render_template('form/program_registration.html', form=form)


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
        # data update logic
        registration.full_name = form.name.data
        registration.program = form.program.data
        registration.phone_number = form.phone.data
        try:
            db.session.commit()
            flash('რეგისტრაცია წარმატებით განახლდა!', 'success')
            return redirect(url_for('user.profile'))
        except Exception as e:
            db.session.rollback()
            flash('დაფიქსირდა შეცდომა რედაქტირებისას.', 'danger')
    elif request.method == 'GET':
        # Filling the form with data retrieved from the database
        form.name.data = registration.full_name
        form.program.data = registration.program
        form.phone.data = registration.phone_number

    form.submit.label.text = "განახლება"

    return render_template('form/edit_registration.html', form=form, registration_id=registration_id)


@form_bp.route('/registration/<int:registration_id>/delete', methods=['POST'])
@login_required
def delete_registration(registration_id):
    # remove logic for program registration
    registration = ProgramRegistration.query.get_or_404(registration_id)

    if registration.user_id != current_user.id:
        abort(403)
    try:
        db.session.delete(registration)
        db.session.commit()
        flash('რეგისტრაცია წარმატებით წაიშალა!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('დაფიქსირდა შეცდომა წაშლისას.', 'danger')
    return redirect(url_for('user.profile'))