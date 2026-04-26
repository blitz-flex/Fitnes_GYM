from ..extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class UserAccount(db.Model, UserMixin):
    __tablename__ = 'user_accounts'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    birthdate = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)
    
    # Fitness Metrics & Settings
    weight = db.Column(db.Float, nullable=True)
    height = db.Column(db.Float, nullable=True)
    fitness_goal = db.Column(db.String(50), nullable=True) # Weight Loss, Muscle Gain, etc.
    activity_level = db.Column(db.String(50), nullable=True) # Sedentary, Active, etc.
    email_notifications = db.Column(db.Boolean, default=False)
    dark_mode = db.Column(db.Boolean, default=False)
    language = db.Column(db.String(10), default='en')
    
    # New Fitness Metrics
    target_weight = db.Column(db.Float, nullable=True)
    fitness_level = db.Column(db.String(50), default='Beginner') # Beginner, Intermediate, Advanced
    gender = db.Column(db.String(20), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    workout_frequency = db.Column(db.Integer, default=3) # Days per week

    # Privacy & AI Preferences
    profile_visibility = db.Column(db.String(20), default='private') # public, friends, private
    weekly_digest = db.Column(db.Boolean, default=True)
    ai_coach_personality = db.Column(db.String(50), default='supportive') # supportive, drill_sergeant, scientific
    sore_muscles = db.Column(db.String(200), default='') # comma-separated list
    
    # Billing & Integrations
    subscription_plan = db.Column(db.String(20), default='free') # free, pro, elite
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    spotify_connected = db.Column(db.Boolean, default=False)
    apple_health_connected = db.Column(db.Boolean, default=False)
    google_fit_connected = db.Column(db.Boolean, default=False)

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    # Relationships
    registrations = db.relationship('ProgramRegistration', back_populates='user', cascade='all, delete-orphan', order_by="desc(ProgramRegistration.created_at)")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        """admin user is determined by username"""
        return self.username in ['admin', 'administrator']

    def get_reset_token(self):
        from flask import current_app
        from itsdangerous import URLSafeTimedSerializer as Serializer
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        from flask import current_app
        from itsdangerous import URLSafeTimedSerializer as Serializer
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt='password-reset-salt', max_age=expires_sec)['user_id']
        except:
            return None
        return UserAccount.query.get(user_id)

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return UserAccount.query.get(int(user_id))