from flask import Flask, render_template, request, redirect, url_for, flash
from forms import ProgramRegistrationForm, SimpleAccountForm
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '25848482828rfrg5rf5'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# --- # --- Helper function to display form errors --- ---
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", 'danger')


@app.route("/")
def index():
    programs = [
        {
            'name': 'იოგა',
            'schedule': 'ორშაბათი / ოთხშაბათი / პარასკევი',
            'time': '10:00 - 11:30',
            'price': '₾80',
            'image': 'yoga.jpg'
        },
        {
            'name': 'კროსფიტი',
            'schedule': 'სამშაბათი / ხუთშაბათი',
            'time': '18:00 - 19:30',
            'price': '₾100',
            'image': 'cros.jpg'
        },
        {
            'name': 'ძალოსნობა',
            'schedule': 'ყოველდღე',
            'time': '12:00 - 22:00',
            'price': '₾120',
            'image': 'Athletics.jpeg'
        },
        {
            'name': 'კრივი',
            'schedule': 'სამშაბათი / ხუთშაბათი / შაბათი',
            'time': '17:00 - 18:30',
            'price': '₾90',
            'image': 'box.jpeg'
        },
        {
            'name': 'პილატესი',
            'schedule': 'ორშაბათი / ოთხშაბათი / პარასკევი',
            'time': '19:00 - 20:00',
            'price': '₾85',
            'image': 'pilates.jpeg'
        },
        {
            'name': 'ცურვა',
            'schedule': 'ყოველდღე',
            'time': '09:00 - 21:00',
            'price': '₾150',
            'image': 'sw.jpg'
        }
    ]
    return render_template("index.html", programs=programs)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/form", methods=['GET', 'POST'])
def form():
    program_form = ProgramRegistrationForm(prefix='program')
    simple_form = SimpleAccountForm(prefix='simple')
    active_form_id = None

    if request.method == 'POST':
        form_type_submitted = request.form.get('form_type')

        if form_type_submitted == 'program':
            if program_form.validate_on_submit():
                #  Data processing
                print(f"პროგრამა: {program_form.name.data}, {program_form.program.data}, {program_form.phone.data}")
                flash('პროგრამაზე რეგისტრაცია წარმატებით დასრულდა!', 'success')
                return redirect(url_for('form'))
            else:
                active_form_id = 'programForm'
                flash_errors(program_form)

        elif form_type_submitted == 'simple':
            if simple_form.validate_on_submit():
                filename = None
                if simple_form.profile_image.data:
                    profile_image_file = simple_form.profile_image.data
                    filename = secure_filename(profile_image_file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    profile_image_file.save(filepath)

                print(f"ანგარიში: {simple_form.name.data}, {simple_form.username.data}, სურათი: {filename}")
                flash('ანგარიშის შექმნა წარმატებით დასრულდა!', 'success')
                return redirect(url_for('form'))
            else:
                active_form_id = 'simpleForm'
                flash_errors(simple_form)

    return render_template("form.html", program_form=program_form, simple_form=simple_form, active_form_id=active_form_id)

if __name__ == '__main__':
    app.run(debug=True)