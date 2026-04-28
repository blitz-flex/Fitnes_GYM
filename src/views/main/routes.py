from flask import render_template, session, redirect, request, url_for
from flask_babel import _
from flask_login import current_user
from ...extensions import db
from . import main_bp

@main_bp.route("/set_language/<language>")
def set_language(language):
    # 1. Update session
    session['language'] = language
    
    # 2. Update user profile if logged in
    if current_user.is_authenticated:
        current_user.language = language
        db.session.commit()
        
    return redirect(request.referrer or url_for('main.index'))

@main_bp.route("/")
def index():
    programs = [
        {'name': _('Yoga'), 'schedule': _('Mon / Wed / Fri'), 'time': '10:00 - 11:30', 'price': '₾80', 'image': 'yoga.jpg'},
        {'name': _('CrossFit'), 'schedule': _('Tue / Thu'), 'time': '18:00 - 19:30', 'price': '₾100', 'image': 'cros.jpg'},
        {'name': _('Strength Training'), 'schedule': _('Every Day'), 'time': '12:00 - 22:00', 'price': '₾120', 'image': 'Athletics.jpeg'},
        {'name': _('Boxing'), 'schedule': _('Tue / Thu / Sat'), 'time': '17:00 - 18:30', 'price': '₾90', 'image': 'box.jpeg'},
        {'name': _('Pilates'), 'schedule': _('Mon / Wed / Fri'), 'time': '19:00 - 20:00', 'price': '₾85', 'image': 'pilates.jpeg'},
        {'name': _('Swimming'), 'schedule': _('Every Day'), 'time': '09:00 - 21:00', 'price': '₾150', 'image': 'sw.jpg'}
    ]
    return render_template("main/index.html", programs=programs)

@main_bp.route("/about")
def about():
    return render_template("main/about.html")



@main_bp.route("/contact")
def contact():
    return render_template("main/contact.html")
