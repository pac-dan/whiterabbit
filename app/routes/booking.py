from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, make_response
from flask_login import login_required, current_user
from app import db, limiter, csrf
from app.models.booking import Booking, BookingStatus
from app.models.package import Package
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import os

booking_bp = Blueprint('booking', __name__)


@booking_bp.route('/')
@login_required
def index():
    """Booking dashboard"""
    upcoming_bookings = Booking.get_upcoming_bookings(user_id=current_user.id)
    past_bookings = Booking.query.filter_by(user_id=current_user.id)\
        .filter(Booking.booking_date < datetime.utcnow())\
        .order_by(Booking.booking_date.desc())\
        .limit(5)\
        .all()

    return render_template(
        'booking/index.html',
        upcoming_bookings=upcoming_bookings,
        past_bookings=past_bookings
    )


@booking_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_booking():
    """Create a new booking"""
    # Get all available packages
    packages = Package.get_active_packages()

    # Get selected package if specified
    package_id = request.args.get('package_id', type=int)
    selected_package = None
    if package_id:
        selected_package = Package.query.get(package_id)

    return render_template(
        'booking/new.html',
        packages=packages,
        selected_package=selected_package
    )


@booking_bp.route('/create', methods=['POST'])
@login_required
@limiter.limit("10 per hour")
def create_booking():
    """Process booking creation"""
    try:
        package_id = request.form.get('package_id', type=int)
        booking_date_str = request.form.get('booking_date')
        location = request.form.get('location')
        location_details = request.form.get('location_details')
        number_of_riders = request.form.get('number_of_riders', 1, type=int)
        rider_experience = request.form.get('rider_experience')
        special_requests = request.form.get('special_requests')

        # Validate inputs
        if not all([package_id, booking_date_str, location]):
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('booking.new_booking'))

        # Get package
        package = Package.query.get_or_404(package_id)

        # Parse and validate booking date
        try:
            booking_date = datetime.fromisoformat(booking_date_str)
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('booking.new_booking'))

        # Check if date is in the future
        min_booking_time = datetime.utcnow() + timedelta(hours=current_app.config['BOOKING_BUFFER_HOURS'])
        if booking_date < min_booking_time:
            flash(f'Bookings must be at least {current_app.config["BOOKING_BUFFER_HOURS"]} hours in advance.', 'danger')
            return redirect(url_for('booking.new_booking'))

        # Check if date is not too far in the future
        max_booking_time = datetime.utcnow() + timedelta(days=current_app.config['BOOKING_ADVANCE_DAYS'])
        if booking_date > max_booking_time:
            flash(f'Bookings can only be made up to {current_app.config["BOOKING_ADVANCE_DAYS"]} days in advance.', 'danger')
            return redirect(url_for('booking.new_booking'))

        # Check if slot is available
        if not Booking.is_slot_available(booking_date, package_id):
            flash('This time slot is no longer available. Please choose a different time.', 'warning')
            return redirect(url_for('booking.new_booking'))

        # Create booking
        booking = Booking(
            user_id=current_user.id,
            package_id=package_id,
            booking_date=booking_date,
            location=location,
            location_details=location_details,
            amount=package.price,
            currency='USD',
            number_of_riders=number_of_riders,
            rider_experience=rider_experience,
            special_requests=special_requests,
            status=BookingStatus.PENDING.value
        )

        db.session.add(booking)
        db.session.commit()

        flash('Booking created! Please proceed to payment.', 'success')
        return redirect(url_for('booking.payment', booking_id=booking.id))

    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.warning(f'Double-booking attempt prevented: package_id={package_id}, date={booking_date_str}')
        flash('This time slot was just booked by someone else. Please choose a different time.', 'warning')
        return redirect(url_for('booking.new_booking', package_id=package_id))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Booking creation error: {str(e)}')
        flash('An error occurred while creating your booking. Please try again.', 'danger')
        return redirect(url_for('booking.new_booking'))


@booking_bp.route('/<int:booking_id>')
@login_required
def view_booking(booking_id):
    """View booking details"""
    booking = Booking.query.get_or_404(booking_id)

    # Ensure user owns this booking or is admin
    if booking.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to view this booking.', 'danger')
        return redirect(url_for('booking.index'))

    return render_template('booking/view.html', booking=booking)


@booking_bp.route('/<int:booking_id>/payment', methods=['GET', 'POST'])
@login_required
def payment(booking_id):
    """Payment page for booking"""
    import stripe  # Import here to avoid module-level issues
    
    booking = Booking.query.get_or_404(booking_id)

    # Ensure user owns this booking
    if booking.user_id != current_user.id:
        flash('You do not have permission to access this booking.', 'danger')
        return redirect(url_for('booking.index'))

    # Check if already paid
    if booking.status != BookingStatus.PENDING.value:
        flash('This booking has already been processed.', 'info')
        return redirect(url_for('booking.view_booking', booking_id=booking.id))

    # Check Stripe configuration
    stripe_secret = current_app.config.get('STRIPE_SECRET_KEY')
    stripe_publishable = current_app.config.get('STRIPE_PUBLISHABLE_KEY')
    
    if not stripe_secret or not stripe_publishable:
        flash('Payment system is not configured. Please contact support.', 'danger')
        return redirect(url_for('booking.index'))

    # Initialize Stripe
    stripe.api_key = stripe_secret

    # Render template with no-cache headers to prevent browser caching
    response = make_response(render_template(
        'booking/payment.html',
        booking=booking,
        stripe_publishable_key=stripe_publishable
    ))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@booking_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """Cancel a booking"""
    booking = Booking.query.get_or_404(booking_id)

    # Ensure user owns this booking
    if booking.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to cancel this booking.', 'danger')
        return redirect(url_for('booking.index'))

    # Check if can cancel
    if not booking.can_cancel:
        flash('This booking cannot be cancelled at this time.', 'warning')
        return redirect(url_for('booking.view_booking', booking_id=booking.id))

    # Process refund if payment was made
    refund_processed = False
    if booking.stripe_payment_intent_id and booking.status == BookingStatus.CONFIRMED.value:
        try:
            import stripe  # Import here to avoid module-level issues
            # Initialize Stripe
            stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
            
            if stripe.api_key:
                # Create refund
                refund = stripe.Refund.create(
                    payment_intent=booking.stripe_payment_intent_id,
                    reason='requested_by_customer'
                )
                
                if refund.status == 'succeeded':
                    booking.status = BookingStatus.REFUNDED.value
                    refund_processed = True
                    current_app.logger.info(f'Refund processed for booking {booking.id}')
                else:
                    current_app.logger.warning(f'Refund pending for booking {booking.id}')
                    
        except stripe.error.StripeError as e:
            current_app.logger.error(f'Stripe refund error for booking {booking.id}: {str(e)}')
            flash(f'Booking cancelled but refund processing failed: {str(e)}. Please contact support.', 'warning')
            booking.cancel()
            return redirect(url_for('booking.index'))
    
    # Cancel booking if no payment or refund not needed
    if not refund_processed:
        booking.cancel()

    flash_message = 'Your booking has been cancelled successfully.'
    if refund_processed:
        flash_message += ' A refund has been processed to your original payment method.'
    
    flash(flash_message, 'success')
    return redirect(url_for('booking.index'))


# API endpoints

@booking_bp.route('/api/check-availability', methods=['POST'])
@csrf.exempt
@login_required
def check_availability():
    """Check if a booking slot is available"""
    data = request.get_json()
    booking_date_str = data.get('booking_date')
    
    # Get package_id and convert to int
    package_id_raw = data.get('package_id')
    package_id = int(package_id_raw) if package_id_raw else None

    if not booking_date_str or not package_id:
        return jsonify({'success': False, 'message': 'Missing parameters'}), 400

    try:
        booking_date = datetime.fromisoformat(booking_date_str)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date format'}), 400

    is_available = Booking.is_slot_available(booking_date, package_id)

    return jsonify({
        'success': True,
        'available': is_available,
        'message': 'Slot is available' if is_available else 'Slot is already booked'
    })


@booking_bp.route('/create-checkout-session/<int:booking_id>', methods=['POST'])
@csrf.exempt
@login_required
@limiter.limit("20 per hour")
def create_checkout_session(booking_id):
    """Create a Stripe Checkout Session for booking"""
    import stripe  # Import here to avoid module-level issues
    from stripe.checkout import Session as CheckoutSession
    
    booking = Booking.query.get_or_404(booking_id)

    # Ensure user owns this booking
    if booking.user_id != current_user.id:
        flash('You do not have permission to access this booking.', 'danger')
        return redirect(url_for('booking.index'))

    # Check if already paid
    if booking.status != BookingStatus.PENDING.value:
        flash('This booking has already been processed.', 'info')
        return redirect(url_for('booking.view_booking', booking_id=booking.id))

    try:
        # Initialize Stripe
        stripe_key = current_app.config.get('STRIPE_SECRET_KEY')
        
        if not stripe_key:
            flash('Payment system is not configured. Please contact support.', 'danger')
            return redirect(url_for('booking.index'))
        
        if not (stripe_key.startswith('sk_test_') or stripe_key.startswith('sk_live_')):
            flash('Payment system configuration error. Please contact support.', 'danger')
            return redirect(url_for('booking.index'))
        
        stripe.api_key = stripe_key

        # Create Checkout Session
        session = CheckoutSession.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': booking.currency.lower() if booking.currency else 'usd',
                    'product_data': {
                        'name': f'{booking.package.name} - Momentum Clips',
                        'description': booking.package.description[:500] if booking.package.description else None,
                    },
                    'unit_amount': int(float(booking.amount) * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('booking.payment_success', booking_id=booking.id, _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('booking.payment_cancel', booking_id=booking.id, _external=True),
            client_reference_id=str(booking.id),
            metadata={
                'booking_id': str(booking.id),
                'user_id': str(booking.user_id),
                'package_name': booking.package.name if booking.package else 'Unknown'
            },
        )

        # Redirect to Stripe Checkout
        return redirect(session.url, code=303)

    except stripe.error.StripeError as e:
        current_app.logger.error(f'Stripe error: {str(e)}')
        flash(f'Payment error: {str(e)}', 'danger')
        return redirect(url_for('booking.payment', booking_id=booking.id))
    except Exception as e:
        current_app.logger.exception('Unexpected error creating checkout session')
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('booking.payment', booking_id=booking.id))


@booking_bp.route('/payment/success/<int:booking_id>')
@login_required
def payment_success(booking_id):
    """Payment success callback"""
    import stripe  # Import here to avoid module-level issues
    from stripe.checkout import Session as CheckoutSession
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Ensure user owns this booking
    if booking.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to view this booking.', 'danger')
        return redirect(url_for('booking.index'))
    
    # Get session_id from query params to verify with Stripe
    session_id = request.args.get('session_id')
    
    if session_id:
        try:
            stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
            session = CheckoutSession.retrieve(session_id)
            
            # Verify the session belongs to this booking
            if session.client_reference_id == str(booking.id):
                # Confirm payment if not already confirmed
                if booking.status == BookingStatus.PENDING.value:
                    booking.confirm_payment(
                        payment_intent_id=session.payment_intent,
                        charge_id=session.payment_intent
                    )
                    
                    # Send confirmation email
                    try:
                        from app.services.email_service import EmailService
                        email_service = EmailService()
                        email_service.send_booking_confirmation(booking)
                        current_app.logger.info(f'Confirmation email sent for booking {booking.id}')
                    except Exception as e:
                        current_app.logger.error(f'Failed to send confirmation email for booking {booking.id}: {str(e)}')
        except Exception as e:
            current_app.logger.error(f'Error retrieving checkout session: {str(e)}')
    
    flash('Payment successful! Your booking is confirmed.', 'success')
    return redirect(url_for('booking.view_booking', booking_id=booking.id))


@booking_bp.route('/payment/cancel/<int:booking_id>')
@login_required
def payment_cancel(booking_id):
    """Payment cancel callback"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Ensure user owns this booking
    if booking.user_id != current_user.id:
        flash('You do not have permission to view this booking.', 'danger')
        return redirect(url_for('booking.index'))
    
    flash('Payment was cancelled. You can try again when ready.', 'info')
    return redirect(url_for('booking.payment', booking_id=booking.id))


@booking_bp.route('/webhook/stripe', methods=['POST'])
@csrf.exempt
@limiter.exempt
def stripe_webhook():
    """Handle Stripe webhook events"""
    import stripe  # Import here to avoid module-level issues
    
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    current_app.logger.info(
        "Stripe webhook received",
        extra={
            "has_signature_header": bool(sig_header),
            "payload_len": len(payload) if payload else 0,
        },
    )
    
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    
    if not webhook_secret:
        current_app.logger.warning('Stripe webhook called but STRIPE_WEBHOOK_SECRET not configured')
        return jsonify({'error': 'Webhook not configured'}), 400
    
    try:
        stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        current_app.logger.error(f'Invalid webhook payload: {str(e)}')
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        current_app.logger.error(f'Invalid webhook signature: {str(e)}')
        return jsonify({'error': 'Invalid signature'}), 400

    current_app.logger.info(
        "Stripe webhook verified",
        extra={
            "event_type": event.get("type"),
            "event_id": event.get("id"),
        },
    )
    
    # Handle the event
    event_type = event.get('type')
    obj = (event.get('data') or {}).get('object') or {}

    if event_type in ('checkout.session.completed', 'checkout.session.async_payment_succeeded'):
        booking_id = obj.get('client_reference_id') or (obj.get('metadata') or {}).get('booking_id')
        payment_status = obj.get('payment_status')
        current_app.logger.info(
            "Stripe checkout session event",
            extra={
                "event_type": event_type,
                "booking_id": booking_id,
                "session_id": obj.get("id"),
                "payment_status": payment_status,
            },
        )
        
        if booking_id:
            booking = Booking.query.get(int(booking_id))
            if booking and booking.status == BookingStatus.PENDING.value:
                booking.confirm_payment(
                    payment_intent_id=obj.get('payment_intent'),
                    charge_id=obj.get('payment_intent')
                )
                current_app.logger.info(f'Booking {booking_id} confirmed via webhook (Checkout Session)')
                
                # Send confirmation email to customer
                try:
                    from app.services.email_service import EmailService
                    email_service = EmailService()
                    email_service.send_booking_confirmation(booking)
                    current_app.logger.info(f'Confirmation email sent for booking {booking_id}')
                except Exception as e:
                    current_app.logger.error(f'Failed to send confirmation email for booking {booking_id}: {str(e)}')
                
    elif event_type in ('checkout.session.expired', 'checkout.session.async_payment_failed'):
        booking_id = obj.get('client_reference_id') or (obj.get('metadata') or {}).get('booking_id')
        current_app.logger.warning(f'Checkout session expired for booking {booking_id}')
        
        # TODO: Notify customer of session expiration
    else:
        # Acknowledge but log unhandled event types for diagnosis
        current_app.logger.info(
            "Stripe webhook unhandled event type (acknowledged)",
            extra={"event_type": event_type},
        )
    
    return jsonify({'status': 'success'}), 200


@booking_bp.route('/api/available-dates', methods=['GET'])
@login_required
def get_available_dates():
    """Get available dates for booking"""
    package_id = request.args.get('package_id', type=int)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    if not all([package_id, start_date_str, end_date_str]):
        return jsonify({'success': False, 'message': 'Missing parameters'}), 400

    try:
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date format'}), 400

    # Get all bookings in this date range
    bookings = Booking.get_bookings_by_date_range(start_date, end_date)

    # Filter for this package and confirmed/pending status
    booked_dates = [
        booking.booking_date.isoformat()
        for booking in bookings
        if booking.package_id == package_id and booking.status in [BookingStatus.CONFIRMED.value, BookingStatus.PENDING.value]
    ]

    return jsonify({
        'success': True,
        'booked_dates': booked_dates
    })
