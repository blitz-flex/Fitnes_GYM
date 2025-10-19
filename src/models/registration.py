from ..extensions import db

class ProgramRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    program = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)