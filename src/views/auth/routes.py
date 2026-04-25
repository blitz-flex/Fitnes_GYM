from datetime import date
from flask import render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from . import auth_bp
from .forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm
from ...models.user import UserAccount
from ...extensions import db, oauth, mail
from ...utils import flash_errors, save_picture

@auth_bp.route('/google/')
def google_login():
    if not oauth:
        flash('Google login is not configured. Please install authlib.', 'error')
        return redirect(url_for('auth.login'))
    redirect_uri = url_for('auth.google_authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/google/authorize')
def google_authorize():
    if not oauth:
        return redirect(url_for('auth.login'))
    
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')
    
    if user_info:
        email = user_info['email']
        google_id = user_info['sub']
        
        user = UserAccount.query.filter_by(email=email).first()
        
        if not user:
            import uuid
            email = user_info.get('email')
            username = email.split('@')[0]
            
            # Check if username exists
            existing = UserAccount.query.filter_by(username=username).first()
            if existing:
                username = f"{username}_{uuid.uuid4().hex[:4]}"
                
            # Extract names
            first_name = user_info.get('given_name') or user_info.get('name', 'Google').split(' ')[0]
            last_name = user_info.get('family_name') or (user_info.get('name', '').split(' ')[1] if ' ' in user_info.get('name', '') else 'User')

            user = UserAccount(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                google_id=google_id,
                profile_image=user_info.get('picture'),
                birthdate=date(2000, 1, 1), # Google rarely provides birthdate in basic scopes
                gender=user_info.get('gender', 'Not Specified')
            )
            # Set a random password since the DB column is NOT NULL
            user.set_password(uuid.uuid4().hex)
            db.session.add(user)
            db.session.commit()
        else:
            # Sync existing user info from Google
            if not user.google_id:
                user.google_id = google_id
            
            # Update picture if they don't have one or if it's a google URL
            google_pic = user_info.get('picture')
            if google_pic and (not user.profile_image or user.profile_image.startswith('https://lh3.googleusercontent.com')):
                user.profile_image = google_pic
            
            # Update gender if missing
            google_gender = user_info.get('gender')
            if google_gender and (not user.gender or user.gender == 'Not Specified'):
                user.gender = google_gender
                
            db.session.commit()
                
        login_user(user)
        flash(f'Welcome back, {user.first_name}!', 'success')
        return redirect(url_for('main.index'))
    
    flash('Failed to log in with Google.', 'danger')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        # Check if username or email already exists
        existing_username = UserAccount.query.filter_by(username=form.username.data).first()
        if existing_username:
            flash('This username is already taken. Please choose another.', 'danger')
            return render_template('auth/register.html', form=form)
        
        existing_email = UserAccount.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('This email address is already registered.', 'danger')
            return render_template('auth/register.html', form=form)

        try:
            # Handle profile image upload
            picture_file = None
            if form.profile_image.data:
                picture_file = save_picture(form.profile_image.data)

            # Create new user
            new_user = UserAccount(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
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
            flash('Registration successful! Welcome to Fitness Center.', 'success')
            return redirect(url_for('main.index'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            print(f"Registration error: {str(e)}")

    else:
        # Flash form validation errors
        flash_errors(form)

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = UserAccount.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.index'))
        else:
            if not user:
                flash('No account found with this username.', 'error')
            else:
                flash('Incorrect password. Please try again.', 'error')
    else:
        flash_errors(form)
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_password', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@auth_bp.route("/forgot-password", methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = UserAccount.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html', title='Reset Password', form=form)

@auth_bp.route("/reset-password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = UserAccount.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.forgot_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title='Reset Password', form=form)