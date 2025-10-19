import os
from flask import Flask

def create_app():

    app = Flask('src', instance_relative_config=True)

    app.config.from_object('src.config.Config')

    # instance და upload create
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    from .extensions import db, migrate
    db.init_app(app)
    migrate.init_app(app, db)
    # Blueprint
    from .views.main import main_bp
    from .views.form import form_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(form_bp)

    # CLI
    from .commands import init_db_command
    app.cli.add_command(init_db_command)

    return app