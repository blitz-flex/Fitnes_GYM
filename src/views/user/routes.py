import os
from datetime import date
import uuid
from flask import render_template, abort, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import user_bp
from .forms import ProfileUpdateForm
from ...extensions import db
from ...models.user import UserAccount


def save_profile_image(file):
    if not file:
        return None
    
    # Create unique filename
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex[:16]}_{filename}"
    
    # Ensure upload directory exists
    upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
        
    file.save(os.path.join(upload_path, unique_filename))
    return unique_filename


@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileUpdateForm()
    
    if form.validate_on_submit():
        # Update user fields
        name_parts = form.name.data.strip().split(' ', 1)
        current_user.first_name = name_parts[0]
        current_user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        current_user.birthdate = form.birthdate.data
        current_user.gender = form.gender.data
        
        # Recalculate age based on new birthdate
        if current_user.birthdate:
            today = date.today()
            current_user.age = today.year - current_user.birthdate.year - ((today.month, today.day) < (current_user.birthdate.month, current_user.birthdate.day))
        
        # Handle image upload
        if form.profile_image.data:
            # Delete old image if it exists and is not default
            if current_user.profile_image:
                old_path = os.path.join(current_app.root_path, 'static', 'uploads', current_user.profile_image)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except:
                        pass
            
            new_image = save_profile_image(form.profile_image.data)
            current_user.profile_image = new_image
            
        try:
            db.session.commit()
            flash('Profile has been successfully updated!', 'success')
            return redirect(url_for('user.profile'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while saving data.', 'danger')
    
    elif request.method == 'GET':
        # Pre-fill form
        form.name.data = current_user.name
        form.birthdate.data = current_user.birthdate
        form.gender.data = current_user.gender

    program_map = {
        'yoga': 'Yoga',
        'crosfit': 'CrossFit',
        'athletics': 'Athletics',
        'boxing': 'Boxing',
        'pilates': 'Pilates',
        'swimming': 'Swimming',
        'cardio': 'Cardio',
        'fitness': 'Fitness'
    }

    return render_template('user/profile.html', user=current_user, form=form, program_map=program_map)


@user_bp.route('/profile/<int:user_id>')
@login_required
def view_user_profile(user_id):
    # Only allow admins to view other users' profiles
    if not current_user.is_admin:
        abort(403)

    user = UserAccount.query.get_or_404(user_id)
    form = ProfileUpdateForm() # Pass form to avoid UndefinedError in template

    program_map = {
        'yoga': 'Yoga',
        'crosfit': 'CrossFit',
        'athletics': 'Athletics',
        'boxing': 'Boxing',
        'pilates': 'Pilates',
        'swimming': 'Swimming'
    }

    return render_template('user/profile.html', user=user, program_map=program_map)


@user_bp.route('/registrations')
@login_required
def registrations():
    program_map = {
        'yoga': 'Yoga',
        'crosfit': 'CrossFit',
        'athletics': 'Athletics',
        'boxing': 'Boxing',
        'pilates': 'Pilates',
        'swimming': 'Swimming',
        'cardio': 'Cardio',
        'fitness': 'Fitness'
    }
    return render_template('user/registrations.html', user=current_user, program_map=program_map)

@user_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    from .forms import SettingsForm, SecurityForm, DeleteAccountForm
    form = SettingsForm()
    security_form = SecurityForm()
    delete_form = DeleteAccountForm()
    
    if request.method == 'POST':
        # Handle Settings Update
        if 'submit' in request.form and form.validate_on_submit():
            try:
                current_user.weight = float(form.weight.data) if form.weight.data else None
                current_user.height = float(form.height.data) if form.height.data else None
                current_user.target_weight = float(form.target_weight.data) if form.target_weight.data else None
                current_user.age = int(form.age.data) if form.age.data else None
                current_user.gender = form.gender.data
                current_user.fitness_goal = form.fitness_goal.data
                current_user.activity_level = form.activity_level.data
                current_user.fitness_level = form.fitness_level.data
                current_user.workout_frequency = int(form.workout_frequency.data) if form.workout_frequency.data else 3
                
                # Advanced Settings
                current_user.weekly_digest = form.weekly_digest.data == '1'
                current_user.ai_coach_personality = form.ai_coach_personality.data
                current_user.sore_muscles = form.sore_muscles.data
                
                current_user.email_notifications = form.email_notifications.data == '1'
                current_user.dark_mode = form.dark_mode.data == '1'
                current_user.language = form.language.data
                
                db.session.commit()
                flash('Settings saved successfully!', 'success')
                return redirect(url_for('user.settings'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while saving settings.', 'danger')
                
        # Handle Password & Email Update
        elif 'submit_security' in request.form and security_form.validate_on_submit():
            # If user is OAuth user, they don't have a password to check
            is_oauth = current_user.google_id is not None
            
            password_correct = False
            if is_oauth:
                password_correct = True
            elif security_form.current_password.data and current_user.check_password(security_form.current_password.data):
                password_correct = True
                
            if password_correct:
                # Update Email
                current_user.email = security_form.email.data
                
                # Update Password if provided
                if security_form.new_password.data:
                    current_user.set_password(security_form.new_password.data)
                
                db.session.commit()
                flash('Security settings updated successfully!', 'success')
                return redirect(url_for('user.settings'))
            else:
                if not is_oauth and not security_form.current_password.data:
                    flash('Current password is required to make changes.', 'danger')
                else:
                    flash('Incorrect current password.', 'danger')
                
        # Handle Account Deletion
        elif 'submit_delete' in request.form and delete_form.validate_on_submit():
            if current_user.check_password(delete_form.password.data):
                from flask_login import logout_user
                db.session.delete(current_user)
                db.session.commit()
                logout_user()
                flash('Your account has been permanently deleted.', 'info')
                return redirect(url_for('main.index'))
            else:
                flash('Incorrect password. Account deletion failed.', 'danger')
            
    # GET request pre-fills
    form.weight.data = str(current_user.weight) if current_user.weight else ''
    form.height.data = str(current_user.height) if current_user.height else ''
    form.target_weight.data = str(current_user.target_weight) if current_user.target_weight else ''
    form.age.data = current_user.age
    form.gender.data = current_user.gender or ''
    form.fitness_goal.data = current_user.fitness_goal or ''
    form.activity_level.data = current_user.activity_level or ''
    form.fitness_level.data = current_user.fitness_level or 'Beginner'
    form.workout_frequency.data = current_user.workout_frequency
    
    # Advanced pre-fills
    form.weekly_digest.data = '1' if current_user.weekly_digest else '0'
    form.ai_coach_personality.data = current_user.ai_coach_personality or 'supportive'
    form.sore_muscles.data = current_user.sore_muscles or ''
    
    form.email_notifications.data = '1' if current_user.email_notifications else '0'
    form.dark_mode.data = '1' if current_user.dark_mode else '0'
    form.language.data = current_user.language or 'en'
    
    security_form.email.data = current_user.email
        
    return render_template('user/settings.html', form=form, security_form=security_form, delete_form=delete_form)

@user_bp.route('/export_data')
@login_required
def export_data():
    import pandas as pd
    import io
    from flask import send_file
    
    # Prepare data for Excel
    data = {
        'Category': [
            'Account', 'Account', 'Account',
            'Metrics', 'Metrics', 'Metrics', 'Metrics', 'Metrics', 'Metrics', 'Metrics',
            'Preferences', 'Preferences', 'Preferences', 'Preferences', 'Preferences',
            'Integrations', 'Integrations', 'Integrations'
        ],
        'Field': [
            'Name', 'Email', 'Plan',
            'Weight', 'Height', 'Target Weight', 'Age', 'Gender', 'Fitness Level', 'Goal',
            'Language', 'Dark Mode', 'Email Notifications', 'Weekly Digest', 'AI Personality',
            'Spotify', 'Apple Health', 'Google Fit'
        ],
        'Value': [
            current_user.name, current_user.email, current_user.subscription_plan,
            current_user.weight, current_user.height, current_user.target_weight, current_user.age, current_user.gender, current_user.fitness_level, current_user.fitness_goal,
            current_user.language, current_user.dark_mode, current_user.email_notifications, current_user.weekly_digest, current_user.ai_coach_personality,
            current_user.spotify_connected, current_user.apple_health_connected, current_user.google_fit_connected
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Create Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='User Profile')
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'fitness_data_{current_user.username}.xlsx'
    )

@user_bp.route('/authorize/<app_name>')
@login_required
def authorize_app(app_name):
    if app_name not in ['spotify', 'apple_health', 'google_fit']:
        flash('Invalid app name.', 'danger')
        return redirect(url_for('user.settings'))
    return render_template('user/authorize.html', app_name=app_name)

@user_bp.route('/finalize_integration/<app_name>', methods=['POST'])
@login_required
def finalize_integration(app_name):
    if app_name == 'spotify':
        current_user.spotify_connected = True
    elif app_name == 'apple_health':
        current_user.apple_health_connected = True
    elif app_name == 'google_fit':
        current_user.google_fit_connected = True
    
    db.session.commit()
    flash(f'Successfully connected to {app_name.replace("_", " ").title()}!', 'success')
    return redirect(url_for('user.settings'))

@user_bp.route('/checkout/<plan_name>')
@login_required
def checkout(plan_name):
    prices = {'basic': 80, 'pro': 120, 'elite': 200}
    if plan_name not in prices:
        flash('Invalid plan selected.', 'danger')
        return redirect(url_for('user.settings'))
    
    from .forms import SettingsForm # To get CSRF
    form = SettingsForm()
    return render_template('user/checkout.html', plan_name=plan_name, price=prices[plan_name], form=form)

@user_bp.route('/process_payment/<plan_name>', methods=['POST'])
@login_required
def process_payment(plan_name):
    from datetime import datetime, timedelta
    
    prices = {'basic': 80, 'pro': 120, 'elite': 200}
    if plan_name not in prices:
        flash('Invalid plan.', 'danger')
        return redirect(url_for('user.settings'))
    
    # Simulate payment success
    current_user.subscription_plan = plan_name
    current_user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
    
    db.session.commit()
    flash(f'Successfully upgraded to {plan_name.title()}! Your plan is active until {current_user.subscription_end_date.strftime("%Y-%m-%d")}.', 'success')
    return redirect(url_for('user.settings'))

@user_bp.route('/cancel_subscription', methods=['POST'])
@login_required
def cancel_subscription():
    current_user.subscription_plan = 'free'
    current_user.subscription_end_date = None
    db.session.commit()
    flash('Your subscription has been cancelled. You are now on the Free plan.', 'info')
    return redirect(url_for('user.settings'))

@user_bp.route('/toggle_integration/<integration>', methods=['POST'])
@login_required
def toggle_integration(integration):
    from flask import jsonify
    
    status = False
    if integration == 'spotify':
        current_user.spotify_connected = not current_user.spotify_connected
        status = current_user.spotify_connected
    elif integration == 'apple_health':
        current_user.apple_health_connected = not current_user.apple_health_connected
        status = current_user.apple_health_connected
    elif integration == 'google_fit':
        current_user.google_fit_connected = not current_user.google_fit_connected
        status = current_user.google_fit_connected
    else:
        return jsonify({'success': False, 'message': 'Invalid integration'}), 400
    
    db.session.commit()
    return jsonify({
        'success': True, 
        'connected': status,
        'message': f'{integration.replace("_", " ").title()} connection updated.'
    })

@user_bp.route('/toggle-theme', methods=['POST'])
@login_required
def toggle_theme():
    data = request.get_json()
    is_dark = data.get('dark_mode', False)
    current_user.dark_mode = is_dark
    db.session.commit()
    return {'success': True}
