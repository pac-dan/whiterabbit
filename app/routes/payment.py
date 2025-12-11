"""
Payment routes for Stripe Checkout
Flow: Payment → Waiver → Calendly Booking
"""
import stripe
from flask import Blueprint, redirect, url_for, flash, request, current_app, render_template, session
from app import db, csrf

payment_bp = Blueprint('payment', __name__)

# Package configuration
PACKAGES = {
    'basic': {
        'name': 'Basic Session',
        'price': 15000,  # €150 in cents
        'duration': '2 hours',
        'calendly_url': 'https://calendly.com/mail-kevinjh/2hrs'
    },
    'pro': {
        'name': 'Pro Session',
        'price': 25000,  # €250 in cents
        'duration': '2.5 hours',
        'calendly_url': 'https://calendly.com/mail-kevinjh/new-meeting'
    },
    'expert': {
        'name': 'Expert Session',
        'price': 35000,  # €350 in cents
        'duration': '3 hours',
        'calendly_url': 'https://calendly.com/mail-kevinjh/new-meeting-1'
    }
}


@payment_bp.route('/checkout/<package>')
def checkout(package):
    """Create Stripe Checkout session and redirect to payment"""
    if package not in PACKAGES:
        flash('Invalid package selected.', 'danger')
        return redirect(url_for('main.packages'))
    
    stripe_key = current_app.config.get('STRIPE_SECRET_KEY')
    if not stripe_key:
        flash('Payment system is not configured. Please contact support.', 'danger')
        return redirect(url_for('main.packages'))
    
    stripe.api_key = stripe_key
    pkg = PACKAGES[package]
    
    try:
        # Create Stripe Checkout Session with all payment methods enabled
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': pkg['name'],
                        'description': f"{pkg['duration']} of professional snowboard filming",
                    },
                    'unit_amount': pkg['price'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('payment.success', package=package, _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('payment.cancelled', _external=True),
            metadata={
                'package': package,
                'package_name': pkg['name']
            },
            # Enable additional payment methods
            payment_method_options={
                'card': {
                    'setup_future_usage': None
                }
            },
            # Allow Stripe to show available payment methods based on customer's device
            automatic_tax={'enabled': False},
        )
        
        return redirect(checkout_session.url, code=303)
        
    except stripe.error.StripeError as e:
        current_app.logger.error(f'Stripe Checkout Error: {str(e)}')
        flash('Unable to process payment. Please try again.', 'danger')
        return redirect(url_for('main.packages'))


@payment_bp.route('/success/<package>')
def success(package):
    """Handle successful payment - redirect to waiver"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Invalid payment session.', 'danger')
        return redirect(url_for('main.packages'))
    
    # Verify the payment was successful
    stripe_key = current_app.config.get('STRIPE_SECRET_KEY')
    if stripe_key:
        stripe.api_key = stripe_key
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            if checkout_session.payment_status != 'paid':
                flash('Payment was not completed. Please try again.', 'warning')
                return redirect(url_for('main.packages'))
        except stripe.error.StripeError as e:
            current_app.logger.error(f'Stripe verification error: {str(e)}')
    
    # Store package info in session for waiver flow
    session['paid_package'] = package
    session['payment_session_id'] = session_id
    
    # Redirect to waiver signing
    flash('Payment successful! Please sign the liability waiver to continue.', 'success')
    return redirect(url_for('payment.waiver', package=package))


@payment_bp.route('/waiver/<package>', methods=['GET', 'POST'])
def waiver(package):
    """Display and process liability waiver after payment"""
    if package not in PACKAGES:
        flash('Invalid package.', 'danger')
        return redirect(url_for('main.packages'))
    
    # Check if payment was made
    if session.get('paid_package') != package:
        flash('Please complete payment first.', 'warning')
        return redirect(url_for('payment.checkout', package=package))
    
    pkg = PACKAGES[package]
    
    # Import waiver text
    from app.models.waiver import WAIVER_TEXT
    
    if request.method == 'POST':
        legal_name = request.form.get('legal_name_typed')
        email = request.form.get('email')
        agreed = request.form.get('agree_to_terms')
        
        if not legal_name or not email or not agreed:
            flash('Please fill in all required fields and agree to the terms.', 'danger')
            return render_template('payment/waiver.html', package=package, pkg=pkg, waiver_text=WAIVER_TEXT)
        
        # Store waiver in database
        import hashlib
        from app.models.waiver import Waiver, CURRENT_WAIVER_VERSION
        
        waiver_text_hash = hashlib.sha256(WAIVER_TEXT.encode('utf-8')).hexdigest()
        
        new_waiver = Waiver(
            booking_id=None,  # No booking yet - will be linked when Calendly booking comes through
            client_email=email,
            legal_name_typed=legal_name,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            waiver_version=CURRENT_WAIVER_VERSION,
            waiver_text_hash=waiver_text_hash
        )
        
        db.session.add(new_waiver)
        db.session.commit()
        
        # Clear payment session and redirect to Calendly
        session.pop('paid_package', None)
        session.pop('payment_session_id', None)
        
        flash('Waiver signed successfully! Now select your preferred time slot.', 'success')
        return redirect(pkg['calendly_url'])
    
    return render_template('payment/waiver.html', package=package, pkg=pkg, waiver_text=WAIVER_TEXT)


@payment_bp.route('/cancelled')
def cancelled():
    """Handle cancelled payment"""
    flash('Payment was cancelled. You can try again when you\'re ready.', 'info')
    return redirect(url_for('main.packages'))

