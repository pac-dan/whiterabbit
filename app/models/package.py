from app import db
from datetime import datetime


class Package(db.Model):
    """Package model for service offerings"""

    __tablename__ = 'packages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    # Duration in hours
    duration = db.Column(db.Integer, nullable=False)

    # Features as text (can be JSON or comma-separated)
    features = db.Column(db.Text, nullable=True)

    # Package details
    max_riders = db.Column(db.Integer, default=1)
    includes_drone = db.Column(db.Boolean, default=False)
    includes_editing = db.Column(db.Boolean, default=True)
    video_count = db.Column(db.Integer, default=1)  # Number of edited videos included

    # Availability
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Display order
    display_order = db.Column(db.Integer, default=0)

    # Images
    thumbnail_url = db.Column(db.String(255), nullable=True)
    gallery_images = db.Column(db.Text, nullable=True)  # JSON array of image URLs

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bookings = db.relationship('Booking', backref='package', lazy='dynamic')

    def __repr__(self):
        return f'<Package {self.name}>'

    def to_dict(self):
        """Convert package to dictionary for JSON responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'duration': self.duration,
            'features': self.features.split(',') if self.features else [],
            'max_riders': self.max_riders,
            'includes_drone': self.includes_drone,
            'includes_editing': self.includes_editing,
            'video_count': self.video_count,
            'is_active': self.is_active,
            'thumbnail_url': self.thumbnail_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @property
    def booking_count(self):
        """Get total number of bookings for this package"""
        return self.bookings.count()

    @property
    def total_revenue(self):
        """Calculate total revenue from this package"""
        from app.models.booking import Booking
        completed_bookings = self.bookings.filter(Booking.status == 'completed').count()
        return float(self.price) * completed_bookings

    @staticmethod
    def get_active_packages():
        """Get all active packages ordered by display_order"""
        return Package.query.filter_by(is_active=True).order_by(Package.display_order, Package.price).all()

    @staticmethod
    def get_featured_packages(limit=3):
        """Get featured packages (top 3 by bookings)"""
        from app.models.booking import Booking
        from sqlalchemy import func

        return Package.query.filter_by(is_active=True)\
            .outerjoin(Booking)\
            .group_by(Package.id)\
            .order_by(func.count(Booking.id).desc())\
            .limit(limit)\
            .all()
