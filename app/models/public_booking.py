from app import db
from datetime import datetime


class PublicBooking(db.Model):
    """
    Booking/order record for the public flow:
    Packages -> Stripe -> Waiver -> Calendly

    This intentionally does NOT depend on user login.
    """

    __tablename__ = 'public_bookings'

    id = db.Column(db.Integer, primary_key=True)

    # Customer info (collected at waiver step)
    customer_email = db.Column(db.String(200), nullable=True, index=True)
    customer_name = db.Column(db.String(200), nullable=True)

    # Package info (from our PACKAGES dict + Stripe metadata)
    package_key = db.Column(db.String(50), nullable=False, index=True)
    package_name = db.Column(db.String(200), nullable=False)

    # Money (Stripe uses cents)
    amount_cents = db.Column(db.Integer, nullable=False, default=0)
    currency = db.Column(db.String(10), nullable=False, default='eur')

    # Stripe identifiers
    stripe_checkout_session_id = db.Column(db.String(255), nullable=True, unique=True, index=True)
    stripe_payment_intent_id = db.Column(db.String(255), nullable=True, index=True)
    paid_at = db.Column(db.DateTime, nullable=True)

    # Waiver linkage (latest waiver id for convenience)
    latest_waiver_id = db.Column(db.Integer, nullable=True, index=True)

    # Calendly linkage (best-effort; may be empty if Calendly doesn't return details)
    calendly_invitee_uuid = db.Column(db.String(100), nullable=True, index=True)
    calendly_event_uuid = db.Column(db.String(100), nullable=True, index=True)
    calendly_event_start = db.Column(db.DateTime, nullable=True)
    calendly_timezone = db.Column(db.String(100), nullable=True)
    calendly_location = db.Column(db.String(255), nullable=True)

    # Status in this public flow
    status = db.Column(db.String(40), nullable=False, default='paid', index=True)
    # paid -> waiver_signed -> scheduled -> completed/cancelled (admin-managed after that)

    # Admin-managed fields
    admin_notes = db.Column(db.Text, nullable=True)
    video_links = db.Column(db.Text, nullable=True)  # JSON/text of links
    delivered_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<PublicBooking {self.id} {self.package_key} {self.status}>"


