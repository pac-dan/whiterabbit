from app import db
from datetime import datetime


class Waiver(db.Model):
    """Liability waiver model for legal protection"""

    __tablename__ = 'waivers'

    id = db.Column(db.Integer, primary_key=True)

    # Link to booking (optional - waiver can exist without booking for walk-ins)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=True, index=True)

    # Client information
    client_name = db.Column(db.String(200), nullable=False)  # Name from booking
    client_email = db.Column(db.String(200), nullable=False)  # Email for records

    # Digital signature
    legal_name_signature = db.Column(db.String(200), nullable=False)  # Typed full legal name

    # Verification data (for legal proof)
    ip_address = db.Column(db.String(50), nullable=False)
    user_agent = db.Column(db.String(500), nullable=True)

    # Waiver versioning (important if terms change)
    waiver_version = db.Column(db.String(10), nullable=False, default='1.0')

    # Timestamps
    signed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationship
    booking = db.relationship('Booking', backref=db.backref('waiver', uselist=False))

    def __repr__(self):
        return f'<Waiver {self.id} - {self.client_name} - {self.signed_at}>'

    def to_dict(self):
        """Convert waiver to dictionary for JSON responses"""
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'client_name': self.client_name,
            'client_email': self.client_email,
            'legal_name_signature': self.legal_name_signature,
            'ip_address': self.ip_address,
            'waiver_version': self.waiver_version,
            'signed_at': self.signed_at.isoformat() if self.signed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def get_by_booking(booking_id):
        """Get waiver for a specific booking"""
        return Waiver.query.filter_by(booking_id=booking_id).first()

    @staticmethod
    def is_signed(booking_id):
        """Check if waiver is signed for a booking"""
        return Waiver.query.filter_by(booking_id=booking_id).first() is not None


# Current waiver version - increment when terms change
CURRENT_WAIVER_VERSION = '1.0'

# Waiver text - IMPORTANT: Have this reviewed by a lawyer
WAIVER_TEXT = """
ASSUMPTION OF RISK, WAIVER OF LIABILITY, AND INDEMNITY AGREEMENT

PLEASE READ CAREFULLY BEFORE SIGNING

1. DESCRIPTION OF ACTIVITIES
I am voluntarily participating in snowboard filming and videography services ("Services") provided by Momentum Clips ("Company"). I understand that the Services involve being filmed while snowboarding, skiing, or engaging in other snow sports activities on mountain terrain.

2. ASSUMPTION OF RISK
I acknowledge and understand that participating in snow sports and being filmed while doing so involves INHERENT RISKS that cannot be eliminated regardless of the care taken to avoid injuries. These risks include, but are not limited to:

• Falls, collisions with other participants, obstacles, trees, or terrain features
• Changing weather conditions including snow, ice, fog, and extreme cold
• Variable terrain conditions including moguls, jumps, half-pipes, and unmarked hazards
• Equipment failure or malfunction
• Distraction caused by the filming process
• Physical exertion and fatigue
• Getting lost or separated from the filming crew
• Injuries ranging from minor bruises to catastrophic injury or death

I VOLUNTARILY ASSUME ALL RISKS associated with participation in these activities, whether or not described above.

3. RELEASE AND WAIVER OF LIABILITY
In consideration for being allowed to participate in the Services, I hereby RELEASE, WAIVE, DISCHARGE, AND COVENANT NOT TO SUE Momentum Clips, its owners, directors, officers, employees, agents, contractors, and representatives (collectively "Releasees") from any and all liability, claims, demands, actions, or causes of action arising out of or related to any loss, damage, or injury, including death, that may be sustained by me, or to any property belonging to me, while participating in the Services, WHETHER CAUSED BY THE NEGLIGENCE OF THE RELEASEES OR OTHERWISE.

4. INDEMNIFICATION
I agree to INDEMNIFY AND HOLD HARMLESS the Releasees from any loss, liability, damage, or costs, including court costs and attorney fees, that may be incurred due to my participation in the Services, whether caused by my negligence or otherwise.

5. MEDICAL ACKNOWLEDGMENT
I certify that I am physically fit and have no medical conditions that would prevent my full participation in snow sports activities. I understand that the Company does not provide medical insurance and that I am responsible for my own medical coverage.

6. MEDIA RELEASE
I grant Momentum Clips permission to use any photographs, video footage, or other recordings of me for promotional, commercial, or any other lawful purpose without compensation.

7. GOVERNING LAW
This Agreement shall be governed by and construed in accordance with the laws of the jurisdiction where the Services are provided.

8. ACKNOWLEDGMENT OF UNDERSTANDING
I HAVE READ THIS ASSUMPTION OF RISK, WAIVER OF LIABILITY, AND INDEMNITY AGREEMENT, FULLY UNDERSTAND ITS TERMS, UNDERSTAND THAT I HAVE GIVEN UP SUBSTANTIAL RIGHTS BY SIGNING IT, AND SIGN IT FREELY AND VOLUNTARILY WITHOUT ANY INDUCEMENT.

BY TYPING MY FULL LEGAL NAME BELOW, I ACKNOWLEDGE THAT I HAVE READ, UNDERSTOOD, AND AGREE TO BE BOUND BY ALL OF THE TERMS AND CONDITIONS OF THIS AGREEMENT.
"""

