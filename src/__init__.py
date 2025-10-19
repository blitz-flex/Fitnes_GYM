import os
from flask import Flask

def create_app():
    app = Flask('src', instance_relative_config=True)
    app.config.from_object('src.config.Config')

    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    from .extensions import db, migrate, login_manager
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .models.user import UserAccount
    @login_manager.user_loader
    def load_user(user_id):
        return UserAccount.query.get(int(user_id))

    # Blueprints
    from .views.main import main_bp
    from .views.form import form_bp
    from .views.auth import auth_bp
    from .views.user import user_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(form_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp)

    # CLI Commands
    from .commands import init_db_command
    app.cli.add_command(init_db_command)

    return app