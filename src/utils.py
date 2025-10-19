from flask import flash

def flash_errors(form):

    for field, errors in form.errors.items():
        for error in errors:
            try:

                label = getattr(form, field).label.text
            except AttributeError:

                label = field.replace('_', ' ').title()
            flash(f"{label}: {error}", 'danger')