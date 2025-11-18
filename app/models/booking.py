from app import db
from datetime import datetime
from enum import Enum


class BookingStatus(Enum):
    """Booking status enumeration"""
    PENDING = 'pending'  # Payment pending
    CONFIRMED = 'confirmed'  # Payment received
    IN_PROGRESS = 'in_progress'  # Session in progress
    COMPLETED = 'completed'  # Session completed, video delivered
    CANCELLED = 'cancelled'  # Booking cancelled
    REFUNDED = 'refunded'  # Payment refunded


class Booking(db.Model):
    """Booking model for session reservations"""

    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'), nullable=False, index=True)

    # Booking details
    booking_date = db.Column(db.DateTime, nullable=False, index=True)
    location = db.Column(db.String(200), nullable=False)
    location_details = db.Column(db.Text, nullable=True)  # Meeting point, parking info, etc.

    # Status
    status = db.Column(db.String(20), nullable=False, default=BookingStatus.PENDING.value, index=True)

    # Pricing
    amount = db.Column(db.Numeric(10, 2), nullable=False)  # Locked price at booking time
    currency = db.Column(db.String(3), nullable=False, default='USD')

    # Payment information
    stripe_payment_intent_id = db.Column(db.String(255), nullable=True, unique=True)
    stripe_charge_id = db.Column(db.String(255), nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)

    # Additional details
    number_of_riders = db.Column(db.Integer, default=1)
    special_requests = db.Column(db.Text, nullable=True)
    equipment_notes = db.Column(db.Text, nullable=True)

    # Experience level of riders for preparation
    rider_experience = db.Column(db.String(50), nullable=True)  # Beginner, Intermediate, Advanced

    # Video delivery
    video_links = db.Column(db.Text, nullable=True)  # JSON array of Vimeo/download links
    delivered_at = db.Column(db.DateTime, nullable=True)

    # Internal notes (admin only)
    admin_notes = db.Column(db.Text, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Booking {self.id} - {self.status}>'

    def to_dict(self):
        """Convert booking to dictionary for JSON responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'user_email': self.user.email if self.user else None,
            'package_id': self.package_id,
            'package_name': self.package.name if self.package else None,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'location': self.location,
            'status': self.status,
            'amount': float(self.amount),
            'currency': self.currency,
            'number_of_riders': self.number_of_riders,
            'special_requests': self.special_requests,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None
        }

    @property
    def is_confirmed(self):
        """Check if booking is confirmed"""
        return self.status == BookingStatus.CONFIRMED.value

    @property
    def is_completed(self):
        """Check if booking is completed"""
        return self.status == BookingStatus.COMPLETED.value

    @property
    def is_cancelled(self):
        """Check if booking is cancelled"""
        return self.status == BookingStatus.CANCELLED.value

    @property
    def can_cancel(self):
        """Check if booking can be cancelled"""
        from datetime import datetime, timedelta
        # Can cancel if booking is more than 24 hours away and not already cancelled/refunded
        if self.status in [BookingStatus.CANCELLED.value, BookingStatus.REFUNDED.value]:
            return False
        return self.booking_date > datetime.utcnow() + timedelta(hours=24)

    def confirm_payment(self, payment_intent_id, charge_id=None):
        """Mark booking as confirmed after payment"""
        self.status = BookingStatus.CONFIRMED.value
        self.stripe_payment_intent_id = payment_intent_id
        self.stripe_charge_id = charge_id
        self.paid_at = datetime.utcnow()
        db.session.commit()

    def mark_in_progress(self):
        """Mark booking as in progress"""
        self.status = BookingStatus.IN_PROGRESS.value
        db.session.commit()

    def mark_completed(self, video_links=None):
        """Mark booking as completed"""
        self.status = BookingStatus.COMPLETED.value
        if video_links:
            self.video_links = video_links
        self.delivered_at = datetime.utcnow()
        db.session.commit()

    def cancel(self):
        """Cancel booking"""
        self.status = BookingStatus.CANCELLED.value
        self.cancelled_at = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def get_upcoming_bookings(user_id=None, limit=None):
        """Get upcoming bookings"""
        query = Booking.query.filter(
            Booking.booking_date > datetime.utcnow(),
            Booking.status.in_([BookingStatus.CONFIRMED.value, BookingStatus.PENDING.value])
        )

        if user_id:
            query = query.filter_by(user_id=user_id)

        query = query.order_by(Booking.booking_date)

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def get_bookings_by_date_range(start_date, end_date):
        """Get bookings within a date range"""
        return Booking.query.filter(
            Booking.booking_date >= start_date,
            Booking.booking_date <= end_date
        ).order_by(Booking.booking_date).all()

    @staticmethod
    def is_slot_available(booking_date, package_id):
        """Check if a time slot is available"""
        # Check if there's already a booking at this time
        existing = Booking.query.filter(
            Booking.booking_date == booking_date,
            Booking.package_id == package_id,
            Booking.status.in_([BookingStatus.CONFIRMED.value, BookingStatus.PENDING.value])
        ).first()

        return existing is None
