import os
from flask import Flask

def create_app():
    app = Flask('src', instance_relative_config=True)
    app.config.from_object('src.config.Config')

    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    from .extensions import db, migrate, login_manager, oauth, mail, babel
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    
    from flask import session, request
    from flask_login import current_user
    def get_locale():
        # 1. Check session (Explicit user choice in current session)
        lang = session.get('language')
        if lang:
            return lang
            
        # 2. Check user profile if logged in
        if current_user.is_authenticated and current_user.language:
            return current_user.language
            
        # 3. Fallback to browser header
        return request.accept_languages.best_match(['en', 'ka'])

    babel.init_app(app, locale_selector=get_locale)
    
    @app.context_processor
    def inject_locale():
        return dict(get_locale=get_locale)
    
    if oauth:
        oauth.init_app(app)
        oauth.register(
            name='google',
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'}
        )

    from .models.user import UserAccount
    @login_manager.user_loader
    def load_user(user_id):
        return UserAccount.query.get(int(user_id))

    # Blueprints
    from .views.main import main_bp
    from .views.form import form_bp
    from .views.auth import auth_bp
    from .views.user import user_bp
    from .views.blog import blog_bp
    from .views.admin import admin_bp
    from .views.exercise import exercise_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(form_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(exercise_bp)

    # CLI Commands
    from .commands import init_db_command, init_exercises_command
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_exercises_command)

    return app