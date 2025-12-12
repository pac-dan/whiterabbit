"""
Payment routes for Stripe Checkout
Flow: Payment → Waiver → Calendly Booking
"""
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


def get_stripe():
    """Get configured stripe module"""
    import stripe
    stripe_key = current_app.config.get('STRIPE_SECRET_KEY')
    if stripe_key:
        stripe.api_key = stripe_key
    return stripe


@payment_bp.route('/checkout/<package>')
def checkout(package):
    """Create Stripe Checkout session and redirect to payment"""
    current_app.logger.info(f'Checkout initiated for package: {package}')
    
    if package not in PACKAGES:
        current_app.logger.warning(f'Invalid package: {package}')
        flash('Invalid package selected.', 'danger')
        return redirect(url_for('main.packages'))
    
    stripe_key = current_app.config.get('STRIPE_SECRET_KEY')
    current_app.logger.info(f'Stripe key configured: {bool(stripe_key)}')
    
    if not stripe_key:
        current_app.logger.error('STRIPE_SECRET_KEY not configured')
        flash('Payment system is being configured. Please try again later or contact support.', 'warning')
        return redirect(url_for('main.packages'))
    
    # Validate key format
    if not (stripe_key.startswith('sk_test_') or stripe_key.startswith('sk_live_')):
        current_app.logger.error('Invalid STRIPE_SECRET_KEY format')
        flash('Payment configuration error. Please contact support.', 'danger')
        return redirect(url_for('main.packages'))
    
    pkg = PACKAGES[package]
    
    try:
        # Import stripe and configure (Stripe v7.x works reliably with explicit submodule import)
        import stripe
        from stripe.checkout import Session as CheckoutSession
        stripe.api_key = stripe_key
        current_app.logger.info(f"Stripe version: {getattr(stripe, 'VERSION', 'unknown')}")
        # Safe diagnostics (no secrets): key kind + length can help spot malformed env values
        current_app.logger.info(
            "Stripe key diagnostics",
            extra={
                "stripe_key_kind": ("sk_live" if stripe_key.startswith("sk_live_") else ("sk_test" if stripe_key.startswith("sk_test_") else "other")),
                "stripe_key_len": len(stripe_key) if isinstance(stripe_key, str) else None,
                "stripe_api_key_type": type(getattr(stripe, "api_key", None)).__name__,
            },
        )
        
        # Create Checkout Session
        checkout_session = CheckoutSession.create(
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
        )
        
        current_app.logger.info(f'Checkout session created: {checkout_session.id}')
        return redirect(checkout_session.url, code=303)
        
    except stripe.error.StripeError as e:
        current_app.logger.error(f'Stripe Error: {str(e)}')
        flash('Unable to process payment. Please try again.', 'danger')
        return redirect(url_for('main.packages'))
    except Exception as e:
        # Full traceback is critical here: we are seeing AttributeError post-200 from Stripe,
        # which suggests an internal library issue (not Stripe credentials).
        key_kind = 'sk_live' if stripe_key.startswith('sk_live_') else ('sk_test' if stripe_key.startswith('sk_test_') else 'other')
        current_app.logger.exception(
            'Payment Error (unexpected exception after Stripe call)',
            extra={
                'package': package,
                'stripe_key_kind': key_kind,
                'stripe_key_present': bool(stripe_key),
            },
        )
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
        try:
            import stripe
            stripe.api_key = stripe_key
            from stripe.checkout import Session as CheckoutSession
            checkout_session = CheckoutSession.retrieve(session_id)
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
