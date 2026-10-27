from app import db


class PackageSchedule(db.Model):
    """Optional booking calendar per real catalogue package; no implicit duration mapping."""
    __tablename__ = 'package_schedules'
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'), primary_key=True)
    calendly_url = db.Column(db.String(500), nullable=False, default='')
