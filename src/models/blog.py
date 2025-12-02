from datetime import datetime
from ..extensions import db
from flask_login import current_user

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(300))
    slug = db.Column(db.String(200), unique=True, nullable=False)
    featured_image = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published = db.Column(db.Boolean, default=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user_accounts.id'), nullable=False)
    views = db.Column(db.Integer, default=0)

    # Relationship with User
    author = db.relationship('UserAccount', backref=db.backref('blog_posts', lazy=True))

    def __repr__(self):
        return f'<BlogPost {self.title}>'

    def increment_views(self):
        """Increment post views"""
        self.views += 1
        db.session.commit()

    @property
    def reading_time(self):
        """Calculate approximate reading time"""
        words = len(self.content.split())
        return max(1, words // 200)  # Assuming 200 words per minute

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'excerpt': self.excerpt,
            'slug': self.slug,
            'featured_image': self.featured_image,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'published': self.published,
            'author': self.author.name if self.author else 'Unknown',
            'views': self.views,
            'reading_time': self.reading_time
        }
