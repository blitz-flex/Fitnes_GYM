from ..extensions import db
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime

class ProgramRegistration(db.Model):
    __tablename__ = 'program_registrations'

    id = Column(Integer, primary_key=True)
    # Foreign key to the UserAccount model
    user_id = Column(Integer, ForeignKey('user_accounts.id'), nullable=False)

    # registration details
    full_name = Column(String(100), nullable=False)
    program = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)
    preferred_time = Column(String(50), nullable=True) # New Field
    start_date = Column(String(50), nullable=True) # New Field
    fitness_goal = Column(String(200), nullable=True) 
    experience_level = Column(String(50), nullable=True) 
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Two-way connection to the UserAccount model
    user = db.relationship('UserAccount', back_populates='registrations')

    @property
    def name(self):
        """Alias for full_name to match template expectations"""
        return self.full_name

    @property
    def phone(self):
        """Alias for phone_number to match template expectations"""
        return self.phone_number
