from ..extensions import db
from datetime import date

class UserAccount(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    profile_image = db.Column(db.String(100), nullable=True)