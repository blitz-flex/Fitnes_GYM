# /src/views/form/routes.py
import os
from flask import render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from .forms import ProgramRegistrationForm, SimpleAccountForm  # <-- შესწორებულია
from . import form_bp
from ...utils import flash_errors  # <-- შესწორებულია
from ...extensions import db
from ...models.user import UserAccount
from ...models.registration import ProgramRegistration

@form_bp.route("/form", methods=['GET', 'POST'])
def form():
    program_form = ProgramRegistrationForm(prefix='program')
    simple_form = SimpleAccountForm(prefix='simple')
    active_form_id = request.args.get('form', 'programForm')  # Default to programForm

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'program':
            if program_form.validate_on_submit():
                registration = ProgramRegistration(name=program_form.name.data, 
                                                program=program_form.program.data,
                                                phone=program_form.phone.data)
                db.session.add(registration)
                try:
                    db.session.commit()
                    flash('პროგრამაზე რეგისტრაცია წარმატებით დასრულდა!', 'success')
                    return redirect(url_for('form.form'))
                except Exception as e:
                    db.session.rollback()
                    flash('დაფიქსირდა შეცდომა. გთხოვთ სცადოთ თავიდან.', 'danger')
            else:
                active_form_id = 'programForm'
                flash_errors(program_form)
        elif form_type == 'simple':
            if simple_form.validate_on_submit():
                if UserAccount.query.filter_by(username=simple_form.username.data).first():
                    flash('მომხმარებელი ამ სახელით უკვე არსებობს!', 'danger')
                    active_form_id = 'simpleForm'
                else:
                    filename = None
                    if simple_form.profile_image.data:
                        try:
                            file = simple_form.profile_image.data
                            filename = secure_filename(file.filename)
                            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                            file.save(filepath)
                        except Exception as e:
                            flash('სურათის ატვირთვა ვერ მოხერხდა.', 'danger')
                            active_form_id = 'simpleForm'
                            return render_template('form/form.html', 
                                                program_form=program_form, 
                                                simple_form=simple_form, 
                                                active_form_id=active_form_id)

                    user = UserAccount(name=simple_form.name.data,
                                     username=simple_form.username.data,
                                     password=simple_form.password.data,
                                     birthdate=simple_form.birthdate.data,
                                     gender=simple_form.gender.data,
                                     profile_image=filename)
                    db.session.add(user)
                    try:
                        db.session.commit()
                        flash('ანგარიშის შექმნა წარმატებით დასრულდა!', 'success')
                        return redirect(url_for('form.form'))
                    except Exception as e:
                        db.session.rollback()
                        flash('დაფიქსირდა შეცდომა. გთხოვთ სცადოთ თავიდან.', 'danger')
            else:
                active_form_id = 'simpleForm'
                flash_errors(simple_form)
    
    return render_template('form/form.html', 
                         program_form=program_form, 
                         simple_form=simple_form, 
                         active_form_id=active_form_id)