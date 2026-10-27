"""Guest checkout: DB catalogue -> verified payment -> signed waiver -> scheduling."""
from flask import Blueprint, redirect, url_for, flash, request, current_app, render_template, session, abort
from app import db, csrf
from app.models.public_booking import PublicBooking
from app.models.waiver import Waiver, WAIVER_TEXT, CURRENT_WAIVER_VERSION
from app.models.public_booking_waiver import PublicBookingWaiver
from app.services.checkout_service import catalogue, access_token, order_from_token, verify_payment
from urllib.parse import urlencode
import re
import stripe

payment_bp = Blueprint('payment', __name__)


def _stripe():
    key = current_app.config.get('STRIPE_SECRET_KEY')
    if not key or not key.startswith(('sk_test_', 'sk_live_')):
        raise ValueError('Payments are not configured')
    stripe.api_key = key
    return stripe.checkout.Session


def _order(package, paid=True, signed=False):
    order = order_from_token(request.values.get('token') or session.get('order_token'), package)
    if not order or (paid and not order.paid_at) or (signed and not order.latest_waiver_id):
        abort(403)
    # Ignore no unrelated booking/waiver identifiers: reject old or tampered links explicitly.
    for name, expected in [('booking_id', order.id), ('waiver_id', order.latest_waiver_id)]:
        if request.args.get(name) and request.args.get(name, type=int) != expected:
            abort(403)
    return order


def _snapshot(order):
    pkg = catalogue(order.package_key) or {}
    return dict(pkg, name=order.package_name, price=order.amount_cents,
                calendly_url=pkg.get('calendly_url', ''))


@payment_bp.route('/checkout/<package>')
def checkout(package):
    pkg = catalogue(package)
    if not pkg or pkg['price'] <= 0:
        abort(404)
    order = None
    try:
        gateway = _stripe()
        order = PublicBooking(package_key=str(pkg['id']), package_name=pkg['name'],
                              amount_cents=pkg['price'], currency='eur', status='pending')
        db.session.add(order)
        db.session.commit()
        token = access_token(order)
        checkout_session = gateway.create(
            payment_method_types=['card'], mode='payment', client_reference_id=str(order.id),
            line_items=[{'price_data': {'currency': 'eur', 'unit_amount': order.amount_cents,
                         'product_data': {'name': order.package_name, 'description': pkg['duration']}}, 'quantity': 1}],
            success_url=url_for('payment.success', package=package, token=token, _external=True) + '&session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('payment.cancelled', _external=True),
            metadata={'order_id': str(order.id), 'package': str(pkg['id'])},
            idempotency_key=f'checkout-order-{order.id}')
        order.stripe_checkout_session_id = checkout_session.id
        db.session.commit()
        session['order_token'] = token
        return redirect(checkout_session.url, code=303)
    except (stripe.StripeError, ValueError):
        db.session.rollback()
        current_app.logger.warning('Checkout unavailable; no payment access granted')
        flash('Online payment is unavailable. Please contact us to arrange your session.', 'warning')
        return redirect(url_for('main.contact', subject=f'Book {pkg["name"]}'))


@payment_bp.route('/success/<package>')
def success(package):
    order = _order(package, paid=False)
    session_id = request.args.get('session_id')
    if not session_id or session_id != order.stripe_checkout_session_id:
        abort(403)
    try:
        verified = verify_payment(_stripe().retrieve(session_id))
        if verified.id != order.id:
            abort(403)
    except (stripe.StripeError, ValueError):
        db.session.rollback()
        flash('We could not verify this payment yet. Retry the payment return link or contact us; do not pay again.', 'warning')
        return redirect(url_for('main.contact'))
    session['order_token'] = access_token(order)
    return redirect(url_for('payment.waiver', package=package))


@payment_bp.route('/webhook', methods=['POST'])
@csrf.exempt
def webhook():
    secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    if not secret:
        return {'error': 'Webhook not configured'}, 503
    try:
        event = stripe.Webhook.construct_event(request.get_data(), request.headers.get('Stripe-Signature', ''), secret)
    except (ValueError, stripe.SignatureVerificationError):
        return {'error': 'Invalid signature'}, 400
    if event['type'] in ('checkout.session.completed', 'checkout.session.async_payment_succeeded'):
        payload = event['data']['object']
        if payload.get('payment_status') == 'paid':
            try:
                verify_payment(payload)
            except ValueError:
                db.session.rollback()
                return {'error': 'Payment mismatch'}, 400
    return {'received': True}


@payment_bp.route('/waiver/<package>', methods=['GET', 'POST'])
def waiver(package):
    order = _order(package)
    if order.latest_waiver_id:
        return redirect(url_for('payment.book_time', package=package, token=access_token(order)))
    if request.method == 'POST':
        name = request.form.get('legal_name_typed', '').strip()
        email = request.form.get('email', '').strip().lower()
        if not (3 <= len(name) <= 100 and len(email) <= 200 and re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email)
                and request.form.get('agree_to_terms') == 'on'):
            flash('Enter your full name, a valid email address and accept the waiver.', 'danger')
        else:
            signed = Waiver(client_name=name, client_email=email, legal_name_signature=name,
                            ip_address=request.remote_addr, user_agent=request.headers.get('User-Agent', '')[:500],
                            waiver_version=CURRENT_WAIVER_VERSION)
            db.session.add(signed)
            db.session.flush()
            order.customer_name, order.customer_email = name, email
            order.latest_waiver_id, order.status = signed.id, 'waiver_signed'
            db.session.add(PublicBookingWaiver(public_booking_id=order.id, waiver_id=signed.id))
            db.session.commit()
            return redirect(url_for('payment.book_time', package=package, token=access_token(order)))
    return render_template('payment/waiver.html', package=package, pkg=_snapshot(order), waiver_text=WAIVER_TEXT)


@payment_bp.route('/cancelled')
def cancelled():
    flash('Checkout closed. No booking is confirmed until payment is verified.', 'info')
    return redirect(url_for('main.packages'))


@payment_bp.route('/book-time/<package>')
def book_time(package):
    order = _order(package, signed=True)
    pkg = _snapshot(order)
    calendar = pkg['calendly_url']
    if calendar:
        calendar += ('&' if '?' in calendar else '?') + urlencode({'name': order.customer_name, 'email': order.customer_email})
    return render_template('payment/book_time.html', pkg=pkg, package_key=package,
                           calendly_url=calendar, token=access_token(order), booking=order)


@payment_bp.route('/complete/<package>')
def complete(package):
    order = _order(package, signed=True)
    # A return URL is not proof of a Calendly event. Staff confirms the actual date/time.
    return render_template('payment/complete.html', pkg=_snapshot(order), booking=order,
                           waiver=db.session.get(Waiver, order.latest_waiver_id), package_key=package)
