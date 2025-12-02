from flask import render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from . import auth_bp
from .forms import LoginForm, RegistrationForm
from ...models.user import UserAccount
from ...extensions import db
from ...utils import flash_errors, save_picture

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        # Check if username already exists
        existing_user = UserAccount.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('ეს მომხმარებლის სახელი უკვე არსებობს. სცადეთ სხვა.', 'danger')
            return render_template('auth/register.html', form=form)

        try:
            # Handle profile image upload
            picture_file = None
            if form.profile_image.data:
                picture_file = save_picture(form.profile_image.data)

            # Create new user
            new_user = UserAccount(
                name=form.name.data,
                username=form.username.data,
                birthdate=form.birthdate.data,
                gender=form.gender.data,
                profile_image=picture_file
            )
            new_user.set_password(form.password.data)

            # Save to database
            db.session.add(new_user)
            db.session.commit()

            # Log in the new user
            login_user(new_user)
            return redirect(url_for('user.profile'))

        except Exception as e:
            db.session.rollback()
            flash('რეგისტრაციისას შეცდომა მოხდა. გთხოვთ სცადოთ ხელახლა.', 'danger')
            print(f"Registration error: {str(e)}")

    else:
        # Flash form validation errors
        flash_errors(form)

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.profile'))
    form = LoginForm()
    if form.validate_on_submit():
        user = UserAccount.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('user.profile'))
        else:
            if not user:
                flash('ასეთი მომხმარებლის სახელით მომხმარებელი არ არსებობს.', 'error')
            else:
                flash('არასწორი პაროლი. გთხოვთ სცადოთ ხელახლა.', 'error')
    else:
        flash_errors(form)
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))