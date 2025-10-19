from ..extensions import db
from sqlalchemy import Column, Integer, String, ForeignKey

class ProgramRegistration(db.Model):
    __tablename__ = 'program_registrations'

    id = Column(Integer, primary_key=True)
    # Foreign key to the UserAccount model
    user_id = Column(Integer, ForeignKey('user_accounts.id'), nullable=False)

    # registration details
    full_name = Column(String(100), nullable=False)
    program = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)

    # # Two-way connection to the UserAccount model
    user = db.relationship('UserAccount', back_populates='registrations')