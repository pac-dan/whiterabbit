from app import db


class PublicBookingWaiver(db.Model):
    """Join table to link multiple waiver signatures to a single public booking."""

    __tablename__ = 'public_booking_waivers'

    id = db.Column(db.Integer, primary_key=True)
    public_booking_id = db.Column(db.Integer, db.ForeignKey('public_bookings.id'), nullable=False, index=True)
    waiver_id = db.Column(db.Integer, db.ForeignKey('waivers.id'), nullable=False, index=True, unique=True)


