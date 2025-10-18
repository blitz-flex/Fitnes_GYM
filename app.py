from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

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

@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")


app.run(debug=True)