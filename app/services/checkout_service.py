"""One price source and one idempotent payment verification path."""
from datetime import datetime
from decimal import Decimal
from itsdangerous import URLSafeTimedSerializer, BadSignature
from flask import current_app
from app import db
from app.models.package import Package
from app.models.package_schedule import PackageSchedule
from app.models.public_booking import PublicBooking


def catalogue(key):
    package = db.session.get(Package, int(key)) if str(key).isdigit() else None
    if not package or not package.is_active:
        return None
    calendar = db.session.get(PackageSchedule, package.id)
    return dict(id=package.id, name=package.name,
                price=int(Decimal(str(package.price)) * 100),
                duration=f'{package.duration} hours',
                calendly_url=calendar.calendly_url if calendar else '')


def access_token(order):
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY']).dumps(
        {'order': order.id, 'package': order.package_key}, salt='guest-order-v1')


def order_from_token(token, package):
    try:
        data = URLSafeTimedSerializer(current_app.config['SECRET_KEY']).loads(
            token or '', salt='guest-order-v1', max_age=30 * 86400)
        order = db.session.get(PublicBooking, data['order'])
        if order and data['package'] == order.package_key == str(package):
            return order
    except (BadSignature, KeyError, TypeError):
        pass
    return None


def verify_payment(payload):
    """Never fulfil a different order, amount or currency; duplicate events are harmless."""
    metadata = payload.get('metadata') or {}
    try:
        order = db.session.get(PublicBooking, int(metadata.get('order_id', '')))
    except (ValueError, TypeError):
        raise ValueError('Missing order reference')
    if not order or any((
        payload.get('payment_status') != 'paid',
        payload.get('mode') != 'payment',
        str(payload.get('client_reference_id')) != str(order.id),
        metadata.get('package') != order.package_key,
        payload.get('amount_total') != order.amount_cents,
        payload.get('currency') != order.currency,
        not payload.get('id'),
        order.stripe_checkout_session_id not in (None, payload.get('id')),
    )):
        raise ValueError('Payment does not match this order')
    order.stripe_checkout_session_id = payload['id']
    order.stripe_payment_intent_id = payload.get('payment_intent')
    if not order.paid_at:
        order.paid_at = datetime.utcnow()
        order.status = 'paid'
        customer = payload.get('customer_details') or {}
        order.customer_email = customer.get('email')
        order.customer_name = customer.get('name')
    db.session.commit()
    return order
