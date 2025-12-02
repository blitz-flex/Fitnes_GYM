from flask import render_template, abort
from flask_login import login_required, current_user
from . import user_bp
from ...models.user import UserAccount


@user_bp.route('/profile')
@login_required
def profile():
    # --- test case ---
    print("-----------------------------------------")
    print(f"მიმდინარე მომხმარებელი: {current_user.username}")
    print(f"მომხმარებლის რეგისტრაციები: {current_user.registrations}")
    print(f"რეგისტრაციების რაოდენობა: {len(current_user.registrations)}")
    print("-----------------------------------------")
    # ------------------------------------

    program_map = {
        'yoga': 'იოგა',
        'crosfit': 'კროსფიტი',
        'athletics': 'ძალოსნობა',
        'boxing': 'კრივი',
        'pilates': 'პილატესი',
        'swimming': 'ცურვა'
    }

    return render_template('user/profile.html', user=current_user, program_map=program_map)


@user_bp.route('/profile/<int:user_id>')
@login_required
def view_user_profile(user_id):
    # Only allow admins to view other users' profiles
    if not current_user.is_admin:
        abort(403)

    user = UserAccount.query.get_or_404(user_id)

    program_map = {
        'yoga': 'იოგა',
        'crosfit': 'კროსფიტი',
        'athletics': 'ძალოსნობა',
        'boxing': 'კრივი',
        'pilates': 'პილატესი',
        'swimming': 'ცურვა'
    }

    return render_template('user/profile.html', user=user, program_map=program_map)
