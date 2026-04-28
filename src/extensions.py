from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_babel import Babel

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
babel = Babel()

# Note: Run 'pip install Authlib requests'
try:
    from authlib.integrations.flask_client import OAuth
    oauth = OAuth()
except ImportError:
    oauth = None
login_manager.login_view = 'auth.login'
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"