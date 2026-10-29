"""HTTPS loopback fixture, isolated DB, no live payment or email calls."""
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from werkzeug.serving import make_ssl_devcert

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / '.runs/2026-10-27-functional-site'
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
os.environ.update(FLASK_ENV='production', SECRET_KEY='local-https-fixture-only',
                  DATABASE_URL='sqlite:///:memory:', ANTHROPIC_API_KEY='local-check',
                  MAIL_USERNAME='local@example.test', MAIL_PASSWORD='local-check',
                  STRIPE_SECRET_KEY='', STRIPE_WEBHOOK_SECRET='')
from app import create_app, db
from app.models.user import User
from app.models.package import Package
from app.models.video import Video
from app.models.public_booking import PublicBooking
from app.services.checkout_service import access_token
from config.config import ProductionConfig

# In-memory SQLite uses StaticPool, which has no production pool-size options.
ProductionConfig.SQLALCHEMY_ENGINE_OPTIONS = {}
app = create_app('production')
app.config['MAIL_SUPPRESS_SEND'] = True
with app.app_context():
    user = User(name='Local QA administrator', email='qa@example.test', is_admin=True)
    user.set_password('local-browser-only-123')
    db.session.add(user)
    for index in range(3):
        db.session.add(Package(name=['Mountain Session', 'Crew Session', 'Full Day Session'][index],
            description='Isolated browser fixture, not a published offer.',
            price=[123.45, 234.56, 345.67][index], duration=[2, 4, 6][index],
            features='4K filming, Edited film', is_active=True))
    db.session.add(Video(title='Local QA gallery film', youtube_id='abcdefghijk',
                        is_published=True, is_featured=True))
    db.session.flush()
    orders = [PublicBooking(package_key='1', package_name='Mountain Session', amount_cents=12345,
                          paid_at=datetime.utcnow(), status='paid') for _ in range(4)]
    db.session.add_all(orders)
    db.session.commit()
    (RUN / 'evidence/browser-fixture.json').write_text(json.dumps({
        'base': 'https://127.0.0.1:5003',
        'waivers': ['/payment/waiver/1?token=' + access_token(order) for order in orders],
        'note': 'Seeded paid order only; no actual Stripe transaction. SMTP suppressed.'
    }, indent=2), encoding='utf-8')

cert = make_ssl_devcert(str(RUN / 'evidence/local-certificate'), host='localhost')
app.run(host='127.0.0.1', port=5003, debug=False, use_reloader=False, ssl_context=cert)
