from app import db
from datetime import datetime


class Testimonial(db.Model):
    """Testimonial model for customer reviews"""

    __tablename__ = 'testimonials'

    id = db.Column(db.Integer, primary_key=True)

    # Client information
    client_name = db.Column(db.String(100), nullable=False)
    client_photo_url = db.Column(db.String(255), nullable=True)
    client_location = db.Column(db.String(100), nullable=True)

    # Review content
    testimonial_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars

    # Project details
    project_type = db.Column(db.String(100), nullable=True)  # Package name or custom description
    session_date = db.Column(db.DateTime, nullable=True)

    # Associated booking (optional)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=True)

    # Video link (optional - if they want to showcase their video)
    video_vimeo_id = db.Column(db.String(50), nullable=True)

    # Visibility
    is_featured = db.Column(db.Boolean, default=False, nullable=False, index=True)
    is_published = db.Column(db.Boolean, default=True, nullable=False)

    # Display order
    display_order = db.Column(db.Integer, default=0)

    # Social proof
    verified_purchase = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    booking = db.relationship('Booking', backref='testimonials', foreign_keys=[booking_id])

    def __repr__(self):
        return f'<Testimonial from {self.client_name}>'

    def to_dict(self):
        """Convert testimonial to dictionary for JSON responses"""
        return {
            'id': self.id,
            'client_name': self.client_name,
            'client_photo_url': self.client_photo_url,
            'client_location': self.client_location,
            'testimonial_text': self.testimonial_text,
            'rating': self.rating,
            'project_type': self.project_type,
            'session_date': self.session_date.isoformat() if self.session_date else None,
            'video_vimeo_id': self.video_vimeo_id,
            'is_featured': self.is_featured,
            'verified_purchase': self.verified_purchase,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }

    @property
    def star_rating(self):
        """Get star rating as string (★★★★★)"""
        filled_stars = '★' * self.rating
        empty_stars = '☆' * (5 - self.rating)
        return filled_stars + empty_stars

    @staticmethod
    def get_featured_testimonials(limit=6):
        """Get featured testimonials"""
        return Testimonial.query.filter_by(is_featured=True, is_published=True)\
            .order_by(Testimonial.display_order, Testimonial.created_at.desc())\
            .limit(limit)\
            .all()

    @staticmethod
    def get_recent_testimonials(limit=10):
        """Get most recent testimonials"""
        return Testimonial.query.filter_by(is_published=True)\
            .order_by(Testimonial.created_at.desc())\
            .limit(limit)\
            .all()

    @staticmethod
    def get_by_rating(min_rating=4, limit=None):
        """Get testimonials with minimum rating"""
        query = Testimonial.query.filter(
            Testimonial.is_published == True,
            Testimonial.rating >= min_rating
        ).order_by(Testimonial.created_at.desc())

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def get_average_rating():
        """Calculate average rating from all published testimonials"""
        result = db.session.query(db.func.avg(Testimonial.rating))\
            .filter_by(is_published=True)\
            .scalar()
        return round(float(result), 1) if result else 0.0

    @staticmethod
    def get_rating_distribution():
        """Get count of testimonials by rating"""
        from sqlalchemy import func

        distribution = db.session.query(
            Testimonial.rating,
            func.count(Testimonial.id).label('count')
        ).filter_by(is_published=True)\
            .group_by(Testimonial.rating)\
            .all()

        # Convert to dictionary
        result = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating, count in distribution:
            result[rating] = count

        return result
