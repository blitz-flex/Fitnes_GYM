from flask import render_template, redirect, url_for, flash
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
        if UserAccount.query.filter_by(username=form.username.data).first():
            flash("მომხმარებელი ამ სახელით უკვე არსებობს!", "danger")
            return render_template('auth/register.html', form=form)

        picture_file = None
        if form.profile_image.data:
            picture_file = save_picture(form.profile_image.data)

        new_user = UserAccount(
            name=form.name.data,
            username=form.username.data,
            birthdate=form.birthdate.data,
            gender=form.gender.data,
            profile_image=picture_file
        )
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        try:
            db.session.commit()
            flash(f"ანგარიში წარმატებით შეიქმნა, {form.username.data}!", "success")
            login_user(new_user)
            return redirect(url_for('user.profile'))
        except Exception as e:
            db.session.rollback()
            flash("დაფიქსირდა შეცდომა რეგისტრაციისას, გთხოვთ სცადოთ თავიდან.", "danger")
    else:
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
            flash("ავტორიზაცია წარმატებით გაიარეთ!", "success")
            return redirect(url_for('user.profile'))
        else:
            flash("მომხმარებლის სახელი ან პაროლი არასწორია.", "danger")
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("თქვენ გამოხვედით სისტემიდან.", "info")
    return redirect(url_for('main.index'))