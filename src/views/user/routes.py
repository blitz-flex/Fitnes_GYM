from flask import render_template
from flask_login import login_required, current_user
from . import user_bp


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