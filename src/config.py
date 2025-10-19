import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-secret-key-that-you-should-change')

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, '..', 'instance', 'fitness_club.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'instance', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024