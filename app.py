from flask import Flask, render_template, request, redirect, url_for, flash
from forms import ProgramRegistrationForm, SimpleAccountForm
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)
app.secret_key = '25848482828rfrg5rf5'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness_club.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

### --- Model ---###

class ProgramRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    program = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'ProgramRegistration({self.name}, {self.program})'


class UserAccount(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    profile_image = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'UserAccount({self.name}, {self.username})'

def init_db():
    with app.app_context():
        if not os.path.exists('fitness_club.db'):
            db.create_all()
            print("Created database and tables.")

def create_upload_folder():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

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
        form_type = request.form.get('form_type')

        # Program registration form
        if form_type == 'program':
            if program_form.validate_on_submit():
                registration = ProgramRegistration(
                    name=program_form.name.data,
                    program=program_form.program.data,
                    phone=program_form.phone.data
                )
                db.session.add(registration)
                db.session.commit()

                flash('პროგრამაზე რეგისტრაცია წარმატებით დასრულდა!', 'success')
                return redirect(url_for('form'))
            else:
                active_form_id = 'programForm'
                flash_errors(program_form)

        # user account form
        elif form_type == 'simple':
            if simple_form.validate_on_submit():
                # check if user already exists
                existing_user = UserAccount.query.filter_by(
                    username=simple_form.username.data
                ).first()

                if existing_user:
                    flash('მომხმარებელი უკვე არსებობს!', 'danger')
                    active_form_id = 'simpleForm'
                    return render_template("form.html",
                                           program_form=program_form,
                                           simple_form=simple_form,
                                           active_form_id=active_form_id)

                filename = None
                if simple_form.profile_image.data:
                    file = simple_form.profile_image.data
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)


                user = UserAccount(
                    name=simple_form.name.data,
                    username=simple_form.username.data,
                    password=simple_form.password.data,
                    birthdate=simple_form.birthdate.data,
                    gender=simple_form.gender.data,
                    profile_image=filename
                )
                db.session.add(user)
                db.session.commit()

                flash('ანგარიშის შექმნა წარმატებით დასრულდა!', 'success')
                return redirect(url_for('form'))
            else:
                active_form_id = 'simpleForm'
                flash_errors(simple_form)

    return render_template("form.html",
                           program_form=program_form,
                           simple_form=simple_form,
                           active_form_id=active_form_id)


if __name__ == '__main__':
    init_db()
    create_upload_folder()
    app.run(debug=True)