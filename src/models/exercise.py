from ..extensions import db
import json

class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    force = db.Column(db.String(50))
    level = db.Column(db.String(50))
    mechanic = db.Column(db.String(50))
    equipment = db.Column(db.String(50))
    category = db.Column(db.String(50))
    
    # Storing lists as JSON strings for simplicity in SQLite
    _primary_muscles = db.Column(db.Text, default='[]')
    _secondary_muscles = db.Column(db.Text, default='[]')
    _instructions = db.Column(db.Text, default='[]')
    _images = db.Column(db.Text, default='[]')

    @property
    def primary_muscles(self):
        return json.loads(self._primary_muscles)

    @primary_muscles.setter
    def primary_muscles(self, value):
        self._primary_muscles = json.dumps(value)

    @property
    def secondary_muscles(self):
        return json.loads(self._secondary_muscles)

    @secondary_muscles.setter
    def secondary_muscles(self, value):
        self._secondary_muscles = json.dumps(value)

    @property
    def instructions(self):
        return json.loads(self._instructions)

    @instructions.setter
    def instructions(self, value):
        self._instructions = json.dumps(value)

    @property
    def images(self):
        return json.loads(self._images)

    @images.setter
    def images(self, value):
        self._images = json.dumps(value)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'force': self.force,
            'level': self.level,
            'mechanic': self.mechanic,
            'equipment': self.equipment,
            'category': self.category,
            'primary_muscles': self.primary_muscles,
            'secondary_muscles': self.secondary_muscles,
            'instructions': self.instructions,
            'images': self.images
        }

    def __repr__(self):
        return f'<Exercise {self.name}>'
